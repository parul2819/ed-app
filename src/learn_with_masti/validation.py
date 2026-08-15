import re

from .schemas import Question

_DIRECT_COMPUTATION_RE = re.compile(r"(\d+)\s*([+\-x×*])\s*(\d+)\s*=\s*\?")
_EXPRESSION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([+\-x×*])\s*(\d+(?:\.\d+)?)\s*$")
_NUMBER_RE = re.compile(r"\d+")
_OPERAND_PAIR_RE = re.compile(r"(\d+)\s*[+\-x×*]\s*(\d+)")


def _apply_operator(a: float, op: str, b: float) -> float:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    return a * b  # "x", "×", "*" all mean multiplication


def _evaluate_expression(text: str) -> float | None:
    """Evaluate text as a plain number or a simple "A op B" expression.

    Returns None if text is neither (can't be evaluated, so no comparison
    can be made against it).
    """
    text = text.strip()
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
    """
    problems: list[str] = []

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

    # (b) Exactly one option may evaluate to the correct value. Catches
    # options that are themselves expressions (e.g. "3x8", "4x6", "2x12"
    # for a target of 24) where more than one is mathematically correct.
    target = _evaluate_expression(q.correct_answer)
    if target is not None:
        matching = [opt for opt in q.options if _evaluate_expression(opt) == target]
        if len(matching) != 1:
            problems.append(
                f"expected exactly one option to evaluate to {_format_number(target)}, "
                f"found {len(matching)}: {matching}"
            )

    # (c) Topic digit rules: addition/subtraction operands must be 2-3
    # digits, multiplication operands must be single digits 1-9.
    numbers = _operand_candidates(q)
    if q.topic in ("addition", "subtraction"):
        for num in numbers:
            digits = len(str(num))
            if not (2 <= digits <= 3):
                problems.append(
                    f"{q.topic} operand {num} in question_text has {digits} digit(s); "
                    "expected 2-3 digits"
                )
    elif q.topic == "multiplication":
        for num in numbers:
            if not (1 <= num <= 9):
                problems.append(
                    f"multiplication operand {num} in question_text is not a "
                    "single digit (1-9)"
                )

    # (d) No duplicate options.
    if len(set(q.options)) != len(q.options):
        problems.append("options contain duplicates")

    return problems
