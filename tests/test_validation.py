from learn_with_masti.schemas import Question
from learn_with_masti.validation import validate_question


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


def test_validate_question_rejects_duplicate_options():
    q = _question(
        question_text="Pick the number that matches: 58.",
        options=["58", "58", "60", "61"],
        correct_answer="58",
        explanation_hint="58 matches.",
    )

    problems = validate_question(q)

    assert "options contain duplicates" in problems


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
