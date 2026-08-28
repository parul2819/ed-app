import uuid
from datetime import datetime, timezone

from learn_with_masti.schemas import ComprehensionQuestion, PassageDetail, Question
from learn_with_masti.validation import validate_bank, validate_passage, validate_question


def _question(**overrides):
    defaults = {
        "id": "test_id_0001",
        "topic": "addition",
        "track": "school",
        "difficulty": "easy",
        "question_text": "54 + 38 = ?",
        "options": ["91", "92", "93", "90"],
        "correct_answer": "92",
        "explanation_hint": "54 + 38 = 92.",
    }
    defaults.update(overrides)
    return Question.model_validate(defaults)


def test_validate_question_accepts_valid_direct_computation():
    q = _question()

    assert validate_question(q) == []


def test_validate_question_accepts_valid_word_problem():
    q = _question(
        question_text="Priya has 32 pencils. Her friend gives her 26 more. How many pencils does she have now?",
        options=["57", "58", "59", "56"],
        correct_answer="58",
        explanation_hint="32 + 26 = 58 pencils.",
    )

    assert validate_question(q) == []


def test_validate_question_rejects_wrong_correct_answer_for_direct_computation():
    q = _question(
        question_text="40 + 20 = ?",
        options=["58", "59", "60", "61"],
        correct_answer="59",
        explanation_hint="40 + 20 = 60.",
    )

    problems = validate_question(q)

    assert any("does not match" in p for p in problems)


def test_validate_question_rejects_multiple_correct_options():
    q = _question(
        topic="multiplication",
        question_text="Which expression gives the correct answer?",
        options=["3x8", "4x6", "2x12", "5x5"],
        correct_answer="3x8",
        explanation_hint="3 x 8 = 24.",
    )

    problems = validate_question(q)

    assert len(problems) == 1
    assert "expected exactly one option" in problems[0]
    assert "found 3" in problems[0]


def test_validate_question_accepts_single_correct_option_among_expressions():
    q = _question(
        topic="multiplication",
        question_text="Which expression gives the correct answer?",
        options=["3x8", "4x7", "2x11", "5x4"],
        correct_answer="3x8",
        explanation_hint="3 x 8 = 24.",
    )

    assert validate_question(q) == []


def test_validate_question_rejects_addition_operand_with_too_few_digits():
    q = _question(
        topic="addition",
        question_text="5 + 38 = ?",
        options=["42", "43", "44", "41"],
        correct_answer="43",
        explanation_hint="5 + 38 = 43.",
    )

    problems = validate_question(q)

    assert any("operand 5" in p and "2-3 digits" in p for p in problems)


def test_validate_question_rejects_subtraction_operand_with_too_many_digits():
    q = _question(
        topic="subtraction",
        question_text="1234 - 38 = ?",
        options=["1195", "1196", "1197", "1194"],
        correct_answer="1196",
        explanation_hint="1234 - 38 = 1196.",
    )

    problems = validate_question(q)

    assert any("operand 1234" in p and "2-3 digits" in p for p in problems)


def test_validate_question_rejects_multiplication_operand_not_single_digit():
    q = _question(
        topic="multiplication",
        question_text="12 x 3 = ?",
        options=["34", "35", "36", "37"],
        correct_answer="36",
        explanation_hint="12 x 3 = 36.",
    )

    problems = validate_question(q)

    assert any("operand 12" in p and "single digit" in p for p in problems)


def test_validate_question_ignores_non_operand_numbers_in_olympiad_word_problems():
    # "Week 1"/"Week 2" are ordinal labels, not addition operands — the
    # school-track "check every bare number" heuristic would false-positive
    # on these, so olympiad questions only check numbers in explicit
    # "A op B" expressions.
    q = _question(
        topic="addition",
        track="olympiad",
        question_text=(
            "A school collected 214 kg of paper in Week 1, and 25 kg more "
            "than Week 1 in Week 2. How much did they collect in Week 2?"
        ),
        options=["238", "239", "240", "237"],
        correct_answer="239",
        explanation_hint="214 + 25 = 239 kg.",
    )

    assert validate_question(q) == []


def test_validate_question_still_checks_explicit_expressions_in_olympiad_questions():
    q = _question(
        topic="multiplication",
        track="olympiad",
        question_text="Look at the pattern: 12x5=60, 2x5=10, 3x5=15. What comes next?",
        options=["18", "19", "20", "21"],
        correct_answer="20",
        explanation_hint="4 x 5 = 20.",
    )

    problems = validate_question(q)

    assert any("operand 12" in p and "single digit" in p for p in problems)


def test_validate_question_accepts_valid_multiplication():
    q = _question(
        topic="multiplication",
        question_text="5 x 4 = ?",
        options=["18", "19", "20", "21"],
        correct_answer="20",
        explanation_hint="5 groups of 4 = 20.",
    )

    assert validate_question(q) == []


def test_validate_question_rejects_word_problem_where_hint_contradicts_correct_answer():
    # Observed LLM failure mode: the hint correctly computes the sum, then
    # correct_answer is a different number the direct-computation check in
    # question_text can't see (word problems have no "A + B = ?" text).
    q = _question(
        question_text=(
            "There are 15 apples in a basket. Another basket has 12 apples. "
            "How many apples are there in total?"
        ),
        options=["27", "26", "28", "29"],
        correct_answer="28",
        explanation_hint="15 + 12 = 27, but the correct answer is 28.",
    )

    problems = validate_question(q)

    assert any("does not match" in p and "27" in p for p in problems)


def test_validate_question_rejects_hint_with_labeled_units_contradicting_answer():
    # Real LLM failure mode: hint uses "N unit x M unit = R" phrasing, which
    # the bare-number equation regex can't see through, hiding a wrong answer.
    q = _question(
        topic="multiplication",
        question_text="There are 6 rows of 8 plants. How many plants in total?",
        options=["48", "64", "56", "50"],
        correct_answer="64",
        explanation_hint="6 rows x 8 plants = 48 plants. But the correct answer is 64.",
    )

    problems = validate_question(q)

    assert any("does not match" in p and "48" in p for p in problems)


def test_validate_question_catches_unicode_minus_sign_mismatch():
    q = _question(
        topic="subtraction",
        question_text="Subtract 189 from 342.",
        options=["163", "153", "152", "164"],
        correct_answer="163",
        explanation_hint="342 − 189 = 153. But the correct answer is 163.",
    )

    problems = validate_question(q)

    assert any("does not match" in p and "153" in p for p in problems)


def test_validate_question_rejects_options_with_units():
    q = _question(
        question_text="Ravi has 14 marbles. He gets 17 more. How many marbles does he have now?",
        options=["31 marbles", "21 marbles", "30 marbles", "22 marbles"],
        correct_answer="31 marbles",
        explanation_hint="14 + 17 = 31",
    )

    problems = validate_question(q)

    assert any("31 marbles" in p and "plain number" in p for p in problems)


def test_validate_question_rejects_duplicate_options():
    q = _question(
        question_text="Pick the number that matches: 58.",
        options=["58", "58", "60", "61"],
        correct_answer="58",
        explanation_hint="58 matches.",
    )

    problems = validate_question(q)

    assert "options contain duplicates" in problems


def test_validate_question_rejects_addition_question_filed_as_multiplication():
    # Observed bug: an addition word problem gets filed under topic
    # "multiplication" (bank mixing/generation error).
    q = _question(
        topic="multiplication",
        question_text="45 + 23 = ?",
        options=["66", "67", "68", "69"],
        correct_answer="68",
        explanation_hint="45 + 23 = 68.",
    )

    problems = validate_question(q)

    assert any("addition" in p and "multiplication" in p for p in problems)


def test_validate_question_does_not_flag_missing_number_puzzle_solved_by_inverse_operation():
    # "Missing-number" puzzles are a legitimate olympiad style for addition
    # (see prompts/question_generation_system.txt): the puzzle is filed
    # under "addition" even though solving it requires subtraction, and the
    # hint spells out that subtraction. question_text never states an
    # explicit "A op B = ?" form, so check (f) must not fire off the hint's
    # operator here -- that would false-positive on valid content.
    q = _question(
        topic="addition",
        track="olympiad",
        question_text="Find the missing number: 238 + __ = 500",
        options=["252", "261", "262", "272"],
        correct_answer="262",
        explanation_hint="500 - 238 = 262.",
    )

    assert validate_question(q) == []


def test_validate_question_accepts_matching_topic_and_operation():
    q = _question(
        topic="multiplication",
        question_text="6 x 7 = ?",
        options=["40", "41", "42", "43"],
        correct_answer="42",
        explanation_hint="6 x 7 = 42.",
    )

    assert validate_question(q) == []


def test_validate_bank_flags_duplicate_question_text():
    q1 = _question(id="add_sch_001", question_text="54 + 38 = ?", correct_answer="92")
    q2 = _question(id="add_sch_002", question_text="54 + 38 = ?", correct_answer="92")
    q3 = _question(
        id="add_sch_003",
        question_text="  54   +  38 = ?  ",  # whitespace-insensitive match
        correct_answer="92",
    )
    q4 = _question(
        id="add_sch_004",
        question_text="12 + 34 = ?",
        options=["46", "47", "48", "49"],
        correct_answer="46",
        explanation_hint="12 + 34 = 46.",
    )

    problems = validate_bank([q1, q2, q3, q4])

    assert set(problems.keys()) == {"add_sch_001", "add_sch_002", "add_sch_003"}
    assert all("duplicate" in p for p in problems["add_sch_001"])
    assert "add_sch_004" not in problems


def test_validate_bank_includes_per_question_problems():
    q1 = _question(
        id="add_sch_001",
        question_text="5 + 38 = ?",
        options=["42", "43", "44", "41"],
        correct_answer="43",
        explanation_hint="5 + 38 = 43.",
    )
    q2 = _question(
        id="add_sch_002",
        question_text="12 + 34 = ?",
        options=["46", "47", "48", "49"],
        correct_answer="46",
        explanation_hint="12 + 34 = 46.",
    )

    problems = validate_bank([q1, q2])

    assert "add_sch_001" in problems
    assert any("operand 5" in p for p in problems["add_sch_001"])
    assert "add_sch_002" not in problems


def test_validate_question_does_not_flag_repeated_addition_expansion_in_hint():
    # "4 x 3 = 12 (3+3+3+3=12)" restates the product as repeated addition;
    # the tail fragment "3+3=12" must not be parsed as its own (wrong)
    # 2-operand equation.
    q = _question(
        topic="multiplication",
        question_text="There are 4 baskets with 3 mangoes each. How many mangoes are there in total?",
        options=["10", "11", "12", "13"],
        correct_answer="12",
        explanation_hint="4 x 3 = 12 mangoes (3+3+3+3=12).",
    )

    assert validate_question(q) == []


def test_validate_question_does_not_flag_missing_factor_puzzle():
    # correct_answer is the missing factor itself (8), not the hint's
    # stated product (48) -- a legitimate olympiad "missing-number" style.
    q = _question(
        topic="multiplication",
        track="olympiad",
        question_text="Find the missing number: 6 x __ = 48",
        options=["6", "7", "8", "9"],
        correct_answer="8",
        explanation_hint="6 x 8 = 48.",
    )

    assert validate_question(q) == []


def test_validate_question_uses_labeled_correct_equation_not_last_one():
    # Some generated hints annotate each option's equation with "(correct)"
    # / "(incorrect)"; the labeled equation is authoritative for comparing
    # against correct_answer, not simply whichever equation appears last.
    q = _question(
        question_text="A child has 28 stickers. 12 more stickers are added. How many stickers does the child have now?",
        options=["40", "30", "42", "32"],
        correct_answer="40",
        explanation_hint="28 + 12 = 40 (correct), 28 + 11 = 39 (incorrect)",
    )

    assert validate_question(q) == []


def test_validate_question_still_flags_wrong_labeled_correct_equation():
    q = _question(
        question_text="A child has 28 stickers. 12 more stickers are added. How many stickers does the child have now?",
        options=["40", "39", "42", "32"],
        correct_answer="39",
        explanation_hint="28 + 12 = 40 (correct), 28 + 11 = 39 (incorrect)",
    )

    problems = validate_question(q)

    assert any("does not match" in p and "40" in p for p in problems)


def test_validate_question_rejects_addition_hint_for_multiplication_topic():
    # Regression: mul_sch_056. A pure addition word problem was mis-filed
    # under "multiplication"; question_text has no "A op B = ?" form, so
    # only checking the hint's operation against the topic can catch this.
    q = _question(
        topic="multiplication",
        question_text="A boy has 6 marbles, and his friend has 3 marbles. How many marbles do they have together?",
        options=["9", "10", "12", "14"],
        correct_answer="9",
        explanation_hint="6 marbles + 3 marbles = 9 marbles",
    )

    problems = validate_question(q)

    assert any("addition" in p and "multiplication" in p for p in problems)


def test_validate_question_flags_correct_answer_that_cannot_be_verified():
    # Regression: mul_oly_012. Options/correct_answer are embedded with
    # MCQ-style labels ("(a) 36"), so they can't be parsed as numbers and
    # silently bypass the hint comparison -- that must be flagged, not
    # silently passed.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="super_hard",
        question_text="What is 9 x 4? (a) 36 (b) 37 (c) 38 (d) 39",
        options=["(a) 36", "(b) 37", "(c) 38", "(d) 39"],
        correct_answer="(a) 36",
        explanation_hint="9 x 4 = 36.",
    )

    problems = validate_question(q)

    assert any("could not be verified" in p for p in problems)


def test_validate_question_flags_self_contradictory_hint_phrasing():
    # Regression: mul_oly_041. The hint's own equation is correct (6 x 3 =
    # 18) but it then contradicts itself ("But the correct answer is 12"),
    # which pure arithmetic checks on the equation can't catch.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="pro",
        question_text="A basket has 6 apples. If each apple is divided into 3 parts, how many parts are there in total?",
        options=["18", "24", "12", "36"],
        correct_answer="18",
        explanation_hint="6 apples x 3 parts = 18 parts. But the correct answer is 12, so there is an extra 6 parts.",
    )

    problems = validate_question(q)

    assert any("self-contradictory" in p for p in problems)


def test_validate_question_flags_multi_digit_operand_from_hint_on_olympiad_word_problem():
    # Regression: mul_oly_044. question_text has no explicit "A op B" form
    # (olympiad operand extraction finds nothing there), so the digit rule
    # must also be checked against operands parsed from the hint.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="pro",
        question_text="A class has 10 students. Each student has 3 pencils. How many pencils are there in total?",
        options=["30", "35", "40", "45"],
        correct_answer="30",
        explanation_hint="10 students x 3 pencils = 30 pencils.",
    )

    problems = validate_question(q)

    assert any("operand 10" in p and "single digit" in p for p in problems)


def test_validate_question_flags_hint_with_no_parseable_equation():
    # Regression: mul_oly_047. The hint states the computation in plain
    # prose ("Dividing 9 by 3 gives 3") with no symbolic equation, so it
    # can't be verified -- that must be flagged rather than silently
    # passed, even though correct_answer ("6") is wrong here too.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="pro",
        question_text="A box has 9 marbles. If each box is divided into 3 equal groups, how many marbles are in each group?",
        options=["3", "6", "9", "12"],
        correct_answer="6",
        explanation_hint="Each box has 9 marbles. Dividing 9 by 3 gives 3 marbles per group.",
    )

    problems = validate_question(q)

    assert any("no parseable equation" in p for p in problems)


def test_validate_question_flags_division_hint_that_does_not_match_correct_answer():
    # Regression: mul_oly_053. Division word phrasing ("6 candies / 4
    # candies per child" with an extra "per child" unit word) doesn't
    # parse as a symbolic equation, so it's flagged as unverifiable rather
    # than silently accepting the wrong correct_answer ("12").
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="pro",
        question_text="A box has 6 candies. If each child gets 4 candies, how many children can get candies?",
        options=["12", "10", "15", "14"],
        correct_answer="12",
        explanation_hint="6 candies / 4 candies per child = 1.5 children (round up to 12)",
    )

    problems = validate_question(q)

    assert problems  # flagged, whether via "no parseable equation" or a mismatch


def test_validate_question_does_not_flag_carried_forward_intermediate_result():
    # Regression: mul_oly_063. A two-step multiplication hint's second
    # equation ("30 x 3 = 90") uses the first equation's result (30) as an
    # operand. 30 is a derived intermediate, not an operand the LLM chose,
    # so the digit rule must not flag it -- this was a false positive.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="pro",
        question_text=(
            "A shopkeeper has 5 shelves with 6 boxes on each shelf. Each box "
            "has 3 pens. How many pens are there in total?"
        ),
        options=["89", "90", "91", "88"],
        correct_answer="90",
        explanation_hint="5 x 6 = 30 boxes. 30 x 3 = 90 pens.",
    )

    assert validate_question(q) == []


def test_validate_question_accepts_inline_lettered_choices_resolved_to_expressions():
    # Regression: mul_oly_001. Options and correct_answer are the choice
    # letters themselves ("a"/"b"/"c"/"d"), with the actual expressions
    # inline in question_text ("(a) 3x7 (b) 4x6 ..."). Letters aren't
    # evaluable, so this used to be flagged as unverifiable; the letter
    # must be resolved to its inline expression before checking arithmetic.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="super_hard",
        question_text="Which of these equals 24? (a) 3x7 (b) 4x6 (c) 5x5 (d) 2x9",
        options=["a", "b", "c", "d"],
        correct_answer="b",
        explanation_hint="4 x 6 = 24, so option (b) is correct.",
    )

    assert validate_question(q) == []


def test_validate_question_flags_inline_lettered_choices_with_two_correct_options():
    # Same inline-choice resolution as above, but two choices evaluate to
    # the target (24) -- the exactly-one-correct-option check must run
    # against the resolved expressions, not the bare option letters.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="super_hard",
        question_text="Which of these equals 24? (a) 3x7 (b) 4x6 (c) 4x6 (d) 2x9",
        options=["a", "b", "c", "d"],
        correct_answer="b",
        explanation_hint="4 x 6 = 24, so option (b) is correct.",
    )

    problems = validate_question(q)

    assert any("expected exactly one option" in p and "found 2" in p for p in problems)


def test_validate_question_does_not_flag_carried_forward_result_in_word_problem_hint():
    # Regression: mul_oly_010. The hint computes an intermediate total
    # ("Total pots = 8+3=11") and reuses it as an operand in the next step
    # ("Flowers = 11 x 5 = 55"). 11 is a derived value carried forward from
    # the first equation's result, not an original operand, so it must not
    # be checked against the multiplication topic's single-digit rule.
    q = _question(
        topic="multiplication",
        track="olympiad",
        difficulty="pro",
        question_text=(
            "A gardener has 8 flower pots with 5 flowers in each pot. He adds "
            "3 more pots, each also with 5 flowers. How many flowers are "
            "there in total now?"
        ),
        options=["50", "53", "55", "58"],
        correct_answer="55",
        explanation_hint="Total pots = 8+3=11. Flowers = 11 x 5 = 55.",
    )

    assert validate_question(q) == []


def test_validate_question_reports_multiple_problems_together():
    q = _question(
        topic="addition",
        question_text="5 + 38 = ?",
        options=["42", "42", "44", "41"],
        correct_answer="41",
        explanation_hint="wrong on purpose",
    )

    problems = validate_question(q)

    assert any("does not match" in p for p in problems)
    assert any("operand 5" in p for p in problems)
    assert "options contain duplicates" in problems


# --- validate_passage ---------------------------------------------------
# RANK1_BODY is a real, hand-checked rank-1 passage (word_count=47,
# sentence_count=8, avg words/sentence=5.88, max word length=6) -- every
# test below starts from a fully clean passage and breaks exactly one thing.

RANK1_BODY = (
    "Ravi has a mango tree. It grows near his small house. "
    "The tree is old and tall. Green leaves cover the whole tree. "
    "Fruit grows on it each May. At first the fruit is green. "
    "Soon the mango turns bright yellow. Ravi picks one and eats it."
)


def _comprehension_question(**overrides):
    defaults = dict(
        id=uuid.uuid4(),
        passage_id=uuid.uuid4(),
        question_type="literal_recall",
        question_text="What does Ravi have?",
        options=["Mango tree", "Red car", "Small dog", "Big house"],
        correct_answer="Mango tree",
        explanation_hint="The passage says Ravi has a mango tree.",
    )
    defaults.update(overrides)
    return ComprehensionQuestion(**defaults)


def _clean_rank1_questions():
    stems = [
        ("What does Ravi have?", ["Mango tree", "Red car", "Small dog", "Big house"], "Mango tree"),
        ("Where does the tree grow?", ["House", "Park", "River", "School"], "House"),
        ("What color does mango turn?", ["Yellow", "Blue", "Purple", "Black"], "Yellow"),
        (
            "How is the tree?",
            ["Old and tall", "Short and new", "Thin and small", "New and short"],
            "Old and tall",
        ),
        ("What covers the tree?", ["Green leaves", "Red flowers", "White snow", "Small stones"], "Green leaves"),
        ("When does the fruit grow?", ["May", "July", "January", "October"], "May"),
        ("What does Ravi do with it?", ["Eats it", "Throws it", "Paints it", "Hides it"], "Eats it"),
    ]
    return [
        _comprehension_question(
            question_text=text, options=opts, correct_answer=ans, explanation_hint="See passage."
        )
        for text, opts, ans in stems
    ]


def _passage(**overrides):
    defaults = dict(
        id=uuid.uuid4(),
        subject="english",
        title="The Mango Tree",
        body=RANK1_BODY,
        word_count=47,
        sentence_count=8,
        difficulty_rank=1,
        takeaway="Fruit changes color as it ripens.",
        created_at=datetime.now(timezone.utc),
        questions=_clean_rank1_questions(),
    )
    defaults.update(overrides)
    return PassageDetail(**defaults)


def test_validate_passage_accepts_clean_rank1_passage():
    assert validate_passage(_passage()) == []


def test_validate_passage_rejects_word_count_not_matching_body():
    problems = validate_passage(_passage(word_count=999))

    assert any("word_count is 999" in p and "actually has 47 words" in p for p in problems)


def test_validate_passage_rejects_word_count_outside_rank_range():
    short_body = "Ravi has a mango tree. It is small."
    problems = validate_passage(
        _passage(body=short_body, word_count=len(short_body.split()), sentence_count=2)
    )

    assert any("outside rank 1's range" in p for p in problems)


def test_validate_passage_rejects_sentence_count_not_matching_body():
    problems = validate_passage(_passage(sentence_count=99))

    assert any("sentence_count is 99" in p and "actually has 8 sentences" in p for p in problems)


def test_validate_passage_rejects_average_words_per_sentence_out_of_range():
    problems = validate_passage(_passage(sentence_count=1))

    assert any("average words/sentence" in p for p in problems)


def test_validate_passage_rejects_word_longer_than_rank_max():
    body = RANK1_BODY.replace("mango", "watermelon")
    problems = validate_passage(_passage(body=body, word_count=len(body.split())))

    assert any("longer than rank 1's max" in p for p in problems)


def test_validate_passage_rejects_question_count_outside_rank_range():
    problems = validate_passage(_passage(questions=_clean_rank1_questions()[:3]))

    assert any("passage has 3 questions" in p for p in problems)


def test_validate_passage_rejects_empty_takeaway():
    problems = validate_passage(_passage(takeaway="   "))

    assert "takeaway is empty" in problems


def test_validate_passage_rejects_takeaway_that_restates_the_title():
    problems = validate_passage(
        _passage(title="The Mango Tree", takeaway="This is about the mango tree.")
    )

    assert any("restatement of the title" in p for p in problems)


def test_validate_passage_rejects_disallowed_question_type_for_rank():
    questions = _clean_rank1_questions()
    questions[0] = _comprehension_question(
        question_type="inference",  # not allowed until rank 21+
        question_text=questions[0].question_text,
        options=questions[0].options,
        correct_answer=questions[0].correct_answer,
    )

    problems = validate_passage(_passage(questions=questions))

    assert any("question_type 'inference' is not allowed at rank 1" in p for p in problems)


def test_validate_passage_rejects_stem_over_word_limit_for_low_rank():
    questions = _clean_rank1_questions()
    questions[2] = _comprehension_question(
        question_text="What color does the mango turn after it ripens fully in the sun?",
        options=questions[2].options,
        correct_answer=questions[2].correct_answer,
    )

    problems = validate_passage(_passage(questions=questions))

    assert any("stem has" in p and "over rank 1's limit" in p for p in problems)


def test_validate_passage_rejects_option_over_word_limit_for_low_rank():
    questions = _clean_rank1_questions()
    questions[0] = _comprehension_question(
        question_text=questions[0].question_text,
        options=["A big green mango tree", "Red car", "Small dog", "Big house"],
        correct_answer="A big green mango tree",
    )

    problems = validate_passage(_passage(questions=questions))

    assert any("over rank 1's maximum" in p for p in problems)


def test_validate_passage_rejects_question_that_contains_its_own_answer():
    questions = _clean_rank1_questions()
    questions[0] = _comprehension_question(
        question_text="Does Ravi have a Mango tree?",
        options=questions[0].options,
        correct_answer="Mango tree",
    )

    problems = validate_passage(_passage(questions=questions))

    assert any("contains its own correct_answer" in p for p in problems)


def test_validate_passage_rejects_near_duplicate_questions():
    # Make question 2 a near-duplicate of question 1's stem (rest of the
    # fields don't matter for this check -- only question_text is compared).
    questions = _clean_rank1_questions()
    questions[1] = _comprehension_question(
        question_text="What does Ravi have here?",
        options=questions[1].options,
        correct_answer=questions[1].correct_answer,
    )

    problems = validate_passage(_passage(questions=questions))

    assert any("near-duplicates" in p for p in problems)


def test_validate_passage_reports_multiple_problems_together():
    problems = validate_passage(_passage(word_count=999, takeaway=""))

    assert any("word_count is 999" in p for p in problems)
    assert "takeaway is empty" in problems
