import difflib
import re

from .reading_levels import spec_for_rank
from .schemas import PassageDetail, Question

_OP = r"+\-−x×*÷/"  # ascii -, unicode minus sign, x, unicode times, *, ÷, /
_UNIT_WORD = r"(?:\s+[A-Za-z]+)?"  # optional trailing unit label, e.g. "8 plants"
_DIRECT_COMPUTATION_RE = re.compile(rf"(\d+)\s*([{_OP}])\s*(\d+)\s*=\s*\?")
_HINT_EQUATION_RE = re.compile(
    rf"(\d+){_UNIT_WORD}\s*([{_OP}])\s*(\d+){_UNIT_WORD}\s*=\s*(\d+(?:\.\d+)?)"
)
_GROUPS_OF_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s+groups?\s+of\s+(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_WORD_EQUATION_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s+(plus|minus)\s+(\d+(?:\.\d+)?)\s+is\s+(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_SUBTRACT_FROM_RE = re.compile(
    r"[Ss]ubtract\s+(\d+(?:\.\d+)?)\s+from\s+(\d+(?:\.\d+)?)\s+to\s+get\s+(\d+(?:\.\d+)?)"
)
_CHAIN_STEP_RE = re.compile(
    r"then\s+(subtract|add)\s+(\d+(?:\.\d+)?)\s+to\s+get\s+(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_SELF_CONTRADICTION_RE = re.compile(
    r"\bbut\s+(?:the\s+)?correct\s+answer\s+is\b", re.IGNORECASE
)
_EXPRESSION_RE = re.compile(rf"^\s*(\d+(?:\.\d+)?)\s*([{_OP}])\s*(\d+(?:\.\d+)?)\s*$")
_CURRENCY_PREFIX_RE = re.compile(r"^[₹$]\s*")
_NUMBER_RE = re.compile(r"\d+")
_OPERAND_PAIR_RE = re.compile(rf"(\d+)\s*[{_OP}]\s*(\d+)")
_OPTION_WITH_UNITS_RE = re.compile(r"\d\s+[A-Za-z]")
_LETTER_OPTION_RE = re.compile(r"^[a-dA-D]$")
_INLINE_CHOICE_RE = re.compile(r"\(([a-dA-D])\)\s*([^()]+?)(?=\s*\([a-dA-D]\)|$)")

_TOPIC_OPS = {
    "addition": {"+"},
    "subtraction": {"-", "−"},
    "multiplication": {"x", "×", "*"},
}
_OP_NAME = {
    "+": "addition",
    "-": "subtraction",
    "−": "subtraction",
    "x": "multiplication",
    "×": "multiplication",
    "*": "multiplication",
    "÷": "division",
    "/": "division",
}
# The operation(s) explanation_hint is allowed to demonstrate for a given
# topic: the topic's own operation, plus its inverse (missing-number/
# missing-factor puzzles legitimately solve addition via subtraction, and
# multiplication via division, without being miscategorized).
_TOPIC_ALLOWED_HINT_OP_NAMES = {
    "addition": {"addition", "subtraction"},
    "subtraction": {"subtraction", "addition"},
    "multiplication": {"multiplication", "division"},
}

# An equation extracted from explanation_hint: (a, op, b, c, match, check_digits).
# match is the regex Match that produced it (used to look for a trailing
# "(correct)" label), or None for equations reconstructed from prose/chains.
# check_digits controls whether a/b are checked against the topic's digit
# rule -- multi-step subtraction/addition chains legitimately break a
# computation into single-digit place-value steps, so those are excluded.
_Equation = tuple[float, str, float, float, "re.Match[str] | None", bool]


def _apply_operator(a: float, op: str, b: float) -> float:
    if op == "+":
        return a + b
    if op in ("-", "−"):
        return a - b
    if op in ("÷", "/"):
        return a / b if b != 0 else float("nan")
    return a * b  # "x", "×", "*" all mean multiplication


def _evaluate_expression(text: str) -> float | None:
    """Evaluate text as a plain number or a simple "A op B" expression.

    Returns None if text is neither (can't be evaluated, so no comparison
    can be made against it). A leading currency symbol (e.g. "₹200") is
    stripped first, since the bank uses that style for money word problems.
    """
    text = _CURRENCY_PREFIX_RE.sub("", text.strip())
    try:
        return float(text)
    except ValueError:
        pass

    match = _EXPRESSION_RE.match(text)
    if not match:
        return None
    a_str, op, b_str = match.groups()
    return _apply_operator(float(a_str), op, float(b_str))


def _format_number(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return str(value)


def _extract_subtract_chain(hint: str) -> list[_Equation]:
    """Parse "Subtract A from B to get C[, then subtract/add D to get E]*".

    A common olympiad-hint style for multi-step subtraction: the running
    result carries forward into each "then subtract/add ... to get ..."
    clause. Each step's amount is deliberately excluded from the digit-rule
    check (check_digits=False) since breaking a subtraction into
    single-digit place-value steps is a legitimate strategy, not a
    violation of the topic's operand digit rule.
    """
    start = _SUBTRACT_FROM_RE.search(hint)
    if not start:
        return []
    a_str, b_str, c_str = start.groups()
    prev_result = float(c_str)
    equations: list[_Equation] = [
        (float(b_str), "-", float(a_str), prev_result, None, False)
    ]
    for m in _CHAIN_STEP_RE.finditer(hint, start.end()):
        kind, amount_str, result_str = m.groups()
        op = "-" if kind.lower() == "subtract" else "+"
        result = float(result_str)
        equations.append((prev_result, op, float(amount_str), result, None, False))
        prev_result = result
    return equations


def _extract_hint_equations(hint: str) -> list[_Equation]:
    """Find every "A op B = C" style equation stated in explanation_hint.

    Tries several extraction strategies in order (symbolic expression,
    "N groups of M = R", "A minus/plus B is C", "Subtract A from B to get
    C" chains) and returns the first strategy that finds anything, since a
    hint uses one phrasing style consistently. Returns an empty list if no
    equation can be parsed at all -- callers should treat that as
    suspicious rather than silently passing the question.
    """
    equations: list[_Equation] = []

    # Repeated-addition expansions (e.g. "4 x 3 = 12 (3+3+3+3=12)") can fool
    # the regex into matching a tail fragment like "3+3=12" as if it were
    # its own equation; skip any match immediately preceded by another
    # operator, since that means it's a fragment of a longer chain, not a
    # standalone "A op B = C" statement.
    for m in _HINT_EQUATION_RE.finditer(hint):
        if re.search(rf"[{_OP}]\s*$", hint[: m.start()]):
            continue
        a_str, op, b_str, c_str = m.groups()
        equations.append((float(a_str), op, float(b_str), float(c_str), m, True))
    if equations:
        return equations

    for m in _GROUPS_OF_RE.finditer(hint):
        a_str, b_str, c_str = m.groups()
        equations.append((float(a_str), "x", float(b_str), float(c_str), None, True))
    if equations:
        return equations

    for m in _WORD_EQUATION_RE.finditer(hint):
        a_str, word, b_str, c_str = m.groups()
        op = "+" if word.lower() == "plus" else "-"
        equations.append((float(a_str), op, float(b_str), float(c_str), None, True))
    if equations:
        return equations

    return _extract_subtract_chain(hint)


def _inline_choices(text: str) -> dict[str, str] | None:
    """Parse "(a) expr (b) expr (c) expr (d) expr" labelled choices out of
    question_text (e.g. "Which of these equals 24? (a) 3x7 (b) 4x6 (c) 5x5
    (d) 2x9"). Returns a lowercase-letter -> expression-text mapping, or
    None if the text doesn't contain a full a/b/c/d labelled choice list.
    """
    matches = _INLINE_CHOICE_RE.findall(text)
    choices = {letter.lower(): expr.strip() for letter, expr in matches}
    if not {"a", "b", "c", "d"} <= choices.keys():
        return None
    return choices


def _operand_candidates(q: Question) -> list[int]:
    """Numbers to check against the topic's digit rule.

    "school" questions are simple and mostly literal, so every bare number
    in question_text is a plausible operand. "olympiad" questions (patterns,
    puzzles, multi-step reasoning) are looser — target values ("equals 24"),
    ordinals ("Week 2"), and digit-count descriptors ("two 3-digit numbers")
    get swept up as false positives there, so only numbers that are
    directly part of an explicit "A op B" expression are checked.
    """
    if q.track == "olympiad":
        return [
            int(n)
            for match in _OPERAND_PAIR_RE.finditer(q.question_text)
            for n in match.groups()
        ]
    return [int(m.group()) for m in _NUMBER_RE.finditer(q.question_text)]


def validate_question(q: Question) -> list[str]:
    """Programmatically check a generated question for common LLM mistakes.

    Returns a list of human-readable problem descriptions; an empty list
    means the question passed every check. This is a fast, best-effort
    heuristic pass (stage 1) — the LLM reviewer (stage 2) catches issues
    this can't, like phrasing or age-appropriateness.

    explanation_hint is the primary source of truth here: every question
    has one, and it states the intended computation, so most checks work
    from equations parsed out of it rather than from question_text (which
    for word problems never spells out "A op B = ?").
    """
    problems: list[str] = []

    # Some olympiad questions present choices inline in question_text (e.g.
    # "Which of these equals 24? (a) 3x7 (b) 4x6 (c) 5x5 (d) 2x9") and use
    # the choice letter as both options and correct_answer. Letters aren't
    # themselves evaluable expressions, so resolve them to the expression
    # text they stand for before running any arithmetic checks below.
    inline_choices = None
    if q.options and all(_LETTER_OPTION_RE.match(opt) for opt in q.options):
        inline_choices = _inline_choices(q.question_text)
    if inline_choices:
        resolved_options = [inline_choices.get(opt.lower(), opt) for opt in q.options]
        resolved_correct_answer = inline_choices.get(
            q.correct_answer.lower(), q.correct_answer
        )
    else:
        resolved_options = q.options
        resolved_correct_answer = q.correct_answer

    # (a) For pure-arithmetic questions ("54 + 38 = ?"), correct_answer must
    # be the actual result of that computation.
    direct_match = _DIRECT_COMPUTATION_RE.search(q.question_text)
    if direct_match:
        a_str, op, b_str = direct_match.groups()
        expected = _apply_operator(float(a_str), op, float(b_str))
        actual = _evaluate_expression(q.correct_answer)
        if actual is None or actual != expected:
            problems.append(
                f"correct_answer {q.correct_answer!r} does not match "
                f"{a_str} {op} {b_str} = {_format_number(expected)}"
            )

    # (h) Some generated hints contradict themselves outright (state a
    # result, then say "but the correct answer is <something else>").
    # Flag this unconditionally -- it's a strong, unambiguous signal
    # regardless of whether the stated equation otherwise parses cleanly.
    if _SELF_CONTRADICTION_RE.search(q.explanation_hint):
        problems.append(
            "explanation_hint contains self-contradictory phrasing "
            "('but the correct answer is ...')"
        )

    # (a2)/(f2) explanation_hint conventionally restates the computation as
    # "A op B = C" (e.g. "32 + 26 = 58 pencils."), including for word
    # problems that have no direct-computation form in question_text. Every
    # equation found is checked for internal consistency; correct_answer is
    # compared against the *last* one (the final result) -- unless an
    # equation is explicitly tagged "(correct)" (a style some generated
    # hints use, e.g. "28 + 12 = 40 (correct), 28 + 11 = 39 (incorrect)"),
    # in which case that tagged equation is authoritative. If no equation
    # can be parsed from the hint at all, that's flagged too rather than
    # silently passed -- every question is supposed to have a checkable
    # hint. The final equation's operation is also compared against the
    # declared topic (allowing the topic's legitimate inverse, e.g. a
    # subtraction hint for an addition missing-number puzzle).
    equations = _extract_hint_equations(q.explanation_hint)
    if not equations:
        problems.append("explanation_hint has no parseable equation to verify")
    else:
        for a, op, b, c, _match, _check_digits in equations:
            expected = _apply_operator(a, op, b)
            if c != expected:
                problems.append(
                    f"explanation_hint states {_format_number(a)} {op} {_format_number(b)} "
                    f"= {_format_number(c)}, but {_format_number(a)} {op} {_format_number(b)} "
                    f"= {_format_number(expected)}"
                )

        labeled = next(
            (
                eq
                for eq in equations
                if eq[4] is not None
                and re.match(
                    r"\s*(?:[A-Za-z]+\s*)?\(correct\)",
                    q.explanation_hint[eq[4].end() : eq[4].end() + 20],
                    re.IGNORECASE,
                )
            ),
            None,
        )
        last_a, last_op, last_b, _last_c, _m, _cd = labeled or equations[-1]
        last_expected = _apply_operator(last_a, last_op, last_b)
        actual = _evaluate_expression(resolved_correct_answer)
        if actual is None:
            problems.append(
                f"correct_answer {q.correct_answer!r} could not be verified against "
                f"explanation_hint's {_format_number(last_a)} {last_op} {_format_number(last_b)} "
                f"= {_format_number(last_expected)} (not a plain number/expression)"
            )
        # "Missing-number" puzzles (e.g. "6 x __ = 48") legitimately have
        # correct_answer equal to one of the hint's stated operands (the
        # missing factor, "8"), not the equation's result -- accept either.
        elif actual != last_expected and actual not in (last_a, last_b):
            problems.append(
                f"correct_answer {q.correct_answer!r} does not match "
                f"explanation_hint's {_format_number(last_a)} {last_op} {_format_number(last_b)} "
                f"= {_format_number(last_expected)}"
            )

        # Only the *final* equation's operation needs to match the topic (or
        # its inverse) -- multi-step hints legitimately use a supporting
        # operation en route to the answer (e.g. "6 + 2 = 8 rows. 8 x 7 =
        # 56 plants." for a multiplication-topic question), so checking
        # every equation would false-positive on those.
        last_op_name = _OP_NAME[last_op]
        if last_op_name not in _TOPIC_ALLOWED_HINT_OP_NAMES[q.topic]:
            problems.append(
                f"explanation_hint's final computation is {last_op_name} "
                f"but question is filed under topic {q.topic!r}"
            )

    # (f) The arithmetic operation explicitly written in question_text must
    # match its declared topic (e.g. "54 + 38 = ?" filed under topic
    # "multiplication"). Deliberately does NOT fall back to the
    # explanation_hint's operator: olympiad "missing-number" puzzles (e.g.
    # "238 + __ = 500") are legitimately filed under addition even though
    # solving them requires subtraction, and would otherwise false-positive.
    if direct_match:
        detected_op = direct_match.group(2)
        if detected_op not in _TOPIC_OPS[q.topic]:
            problems.append(
                f"question uses {_OP_NAME[detected_op]} (operator {detected_op!r}) "
                f"but is filed under topic {q.topic!r}"
            )

    # (b) Exactly one option may evaluate to the correct value. Catches
    # options that are themselves expressions (e.g. "3x8", "4x6", "2x12"
    # for a target of 24) where more than one is mathematically correct.
    # Inline-lettered options (e.g. "a"/"b"/"c"/"d") are resolved to the
    # expression each letter stands for first, so this checks the actual
    # inline choices rather than the option letters themselves.
    target = _evaluate_expression(resolved_correct_answer)
    if target is not None:
        matching = [
            opt
            for opt, resolved_opt in zip(q.options, resolved_options)
            if _evaluate_expression(resolved_opt) == target
        ]
        if len(matching) != 1:
            problems.append(
                f"expected exactly one option to evaluate to {_format_number(target)}, "
                f"found {len(matching)}: {matching}"
            )

    # (c) Topic digit rules: addition/subtraction operands must be 2-3
    # digits, multiplication operands must be single digits 1-9. Checked
    # against numbers in question_text (see _operand_candidates) as well as
    # operands of hint equations flagged check_digits=True, for both
    # tracks -- olympiad word problems often state their real operands only
    # in the hint (question_text has no explicit "A op B" form to find them
    # in).
    numbers = set(_operand_candidates(q))
    if equations:
        # Multi-step hints (e.g. "Total pots = 8+3=11. Flowers = 11 x 5 =
        # 55.") carry an earlier equation's result into a later equation as
        # an operand. That carried-in value is a derived intermediate, not
        # an original operand the LLM chose, so it's excluded from the
        # digit-rule check once it's been seen as a prior equation's result
        # (equations appear in the order they're stated in the hint).
        prior_results: set[int] = set()
        for a, _op, b, c, _match, check_digits in equations:
            if check_digits:
                numbers |= {
                    int(n) for n in (a, b) if n == int(n) and int(n) not in prior_results
                }
            if c == int(c):
                prior_results.add(int(c))
    if q.topic in ("addition", "subtraction"):
        for num in sorted(numbers):
            digits = len(str(num))
            if not (2 <= digits <= 3):
                problems.append(
                    f"{q.topic} operand {num} has {digits} digit(s); expected 2-3 digits"
                )
    elif q.topic == "multiplication":
        for num in sorted(numbers):
            if not (1 <= num <= 9):
                problems.append(
                    f"multiplication operand {num} is not a single digit (1-9)"
                )

    # (d) No duplicate options.
    if len(set(q.options)) != len(q.options):
        problems.append("options contain duplicates")

    # (e) Options must be plain numbers (or expressions like "3x8"), never a
    # number with a unit/word attached (e.g. "58 pencils") — matches the
    # question bank's existing style.
    for opt in q.options:
        if _OPTION_WITH_UNITS_RE.search(opt):
            problems.append(f"option {opt!r} should be a plain number, not include units/words")

    return problems


def validate_bank(questions: list[Question]) -> dict[str, list[str]]:
    """Validate every question in a bank file, plus cross-question checks.

    Runs validate_question on each question, then (g) flags question_text
    that is duplicated (case/whitespace-insensitive) elsewhere in the same
    file. Returns a mapping of question id -> problems, containing only ids
    that have at least one problem.
    """
    problems_by_id: dict[str, list[str]] = {}
    for q in questions:
        problems = validate_question(q)
        if problems:
            problems_by_id[q.id] = problems

    ids_by_text: dict[str, list[str]] = {}
    for q in questions:
        key = " ".join(q.question_text.split()).lower()
        ids_by_text.setdefault(key, []).append(q.id)

    for ids in ids_by_text.values():
        if len(ids) < 2:
            continue
        for qid in ids:
            others = [i for i in ids if i != qid]
            problems_by_id.setdefault(qid, []).append(
                f"question_text is a duplicate of {others}"
            )

    return problems_by_id


_WORD_RE = re.compile(r"[A-Za-z']+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_NEAR_DUPLICATE_RATIO = 0.8

# Words ignored when judging whether a passage's takeaway is a real lesson
# or just the title said again -- generic enough to appear in almost any
# title/takeaway pair without indicating actual overlap in content.
_TAKEAWAY_STOPWORDS = {
    "a", "an", "the", "is", "was", "are", "were", "this", "that", "about",
    "of", "to", "and", "in", "on", "how", "why", "it", "its", "for", "with",
}


def _content_words(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in _TAKEAWAY_STOPWORDS}


def _sentence_count(body: str) -> int:
    return len([s for s in _SENTENCE_SPLIT_RE.split(body.strip()) if s.strip()])


def _max_word_length(body: str) -> int:
    return max((len(w) for w in _WORD_RE.findall(body)), default=0)


def validate_passage(p: PassageDetail) -> list[str]:
    """Programmatically check a passage and its comprehension questions
    against the measurable spec for its difficulty_rank (see
    reading_levels.spec_for_rank). Mirrors validate_question's role for the
    maths bank: a fast, best-effort heuristic pass that generation and
    review can both run before content ships.
    """
    problems: list[str] = []
    spec = spec_for_rank(p.difficulty_rank)

    # (a) Declared word_count must match the body's actual word count, and
    # fall within the rank's target range.
    actual_word_count = len(p.body.split())
    if actual_word_count != p.word_count:
        problems.append(
            f"word_count is {p.word_count} but the body actually has "
            f"{actual_word_count} words"
        )
    if not (spec.word_count_min <= p.word_count <= spec.word_count_max):
        problems.append(
            f"word_count {p.word_count} is outside rank {p.difficulty_rank}'s "
            f"range [{spec.word_count_min}, {spec.word_count_max}]"
        )

    # (b) Declared sentence_count must match the body's actual sentence count.
    actual_sentence_count = _sentence_count(p.body)
    if actual_sentence_count != p.sentence_count:
        problems.append(
            f"sentence_count is {p.sentence_count} but the body actually has "
            f"{actual_sentence_count} sentences"
        )

    # (c) Average words/sentence, checked as a float -- never rounded to an
    # integer range (see reading_levels.py for why that matters).
    if p.sentence_count > 0:
        average = p.word_count / p.sentence_count
        if not (spec.words_per_sentence_min <= average <= spec.words_per_sentence_max):
            problems.append(
                f"average words/sentence is {average:.2f}, outside rank "
                f"{p.difficulty_rank}'s range [{spec.words_per_sentence_min}, "
                f"{spec.words_per_sentence_max}]"
            )
    else:
        problems.append("sentence_count is 0; cannot compute average words per sentence")

    # (d) No word in the body may exceed the rank's max letter count.
    longest = _max_word_length(p.body)
    if longest > spec.max_word_length:
        problems.append(
            f"body contains a word of {longest} letters, longer than rank "
            f"{p.difficulty_rank}'s max of {spec.max_word_length}"
        )

    # (e) Question count must fall within the rank's range.
    if not (spec.question_count_min <= len(p.questions) <= spec.question_count_max):
        problems.append(
            f"passage has {len(p.questions)} questions, outside rank "
            f"{p.difficulty_rank}'s range [{spec.question_count_min}, "
            f"{spec.question_count_max}]"
        )

    # (f) takeaway must be present and read like a real lesson, not just the
    # title said back -- flagged when every content word in the title also
    # appears in the takeaway and the takeaway adds fewer than 3 new ones.
    if not p.takeaway.strip():
        problems.append("takeaway is empty")
    else:
        title_words = _content_words(p.title)
        takeaway_words = _content_words(p.takeaway)
        extra_words = takeaway_words - title_words
        if title_words and title_words <= takeaway_words and len(extra_words) < 3:
            problems.append(
                "takeaway looks like a restatement of the title rather than a real lesson"
            )

    # Per-question checks.
    normalized_stems: list[str] = []
    for idx, question in enumerate(p.questions, start=1):
        # (g) correct_answer must be one of options (the ComprehensionQuestion
        # schema already enforces this at construction; checked again here
        # for a complete, self-contained report).
        if question.correct_answer not in question.options:
            problems.append(
                f"question {idx}: correct_answer {question.correct_answer!r} "
                "is not among its options"
            )

        # (h) question_type must be one this rank allows.
        if question.question_type not in spec.allowed_question_types:
            problems.append(
                f"question {idx}: question_type {question.question_type!r} is not allowed "
                f"at rank {p.difficulty_rank} (allowed: {spec.allowed_question_types})"
            )

        # (i) stem/option word-length limits, where the band sets them
        # (only ranks 1-10 do -- see reading_levels.QuestionTypeBand).
        stem_word_count = len(question.question_text.split())
        if spec.stem_max_words is not None and stem_word_count > spec.stem_max_words:
            problems.append(
                f"question {idx}: stem has {stem_word_count} words, over rank "
                f"{p.difficulty_rank}'s limit of {spec.stem_max_words}"
            )
        for opt in question.options:
            opt_word_count = len(opt.split())
            if spec.option_min_words is not None and opt_word_count < spec.option_min_words:
                problems.append(
                    f"question {idx}: option {opt!r} has {opt_word_count} words, under "
                    f"rank {p.difficulty_rank}'s minimum of {spec.option_min_words}"
                )
            if spec.option_max_words is not None and opt_word_count > spec.option_max_words:
                problems.append(
                    f"question {idx}: option {opt!r} has {opt_word_count} words, over "
                    f"rank {p.difficulty_rank}'s maximum of {spec.option_max_words}"
                )

        # (j) the stem must not give away its own answer.
        answer = question.correct_answer.strip()
        if answer and re.search(rf"\b{re.escape(answer)}\b", question.question_text, re.IGNORECASE):
            problems.append(
                f"question {idx}: stem contains its own correct_answer {answer!r}"
            )

        normalized_stems.append(" ".join(question.question_text.lower().split()))

    # (k) no two questions in the same passage may be near-duplicates.
    for i in range(len(normalized_stems)):
        for j in range(i + 1, len(normalized_stems)):
            ratio = difflib.SequenceMatcher(None, normalized_stems[i], normalized_stems[j]).ratio()
            if ratio > _NEAR_DUPLICATE_RATIO:
                problems.append(
                    f"questions {i + 1} and {j + 1} are near-duplicates "
                    f"(similarity {ratio:.2f})"
                )

    return problems
