import uuid

import pytest
from pydantic import ValidationError

from learn_with_masti.schemas import (
    ComprehensionQuestion,
    GetSolutionRequest,
    PassageDetail,
    PassageSummary,
    Question,
)


def make_question(**overrides):
    data = dict(
        id="add_sch_001",
        topic="addition",
        track="school",
        difficulty="easy",
        question_text="2 + 2 = ?",
        options=["3", "4", "5", "6"],
        correct_answer="4",
        explanation_hint="2+2=4",
    )
    data.update(overrides)
    return data


def test_question_accepts_valid_data():
    q = Question(**make_question())
    assert q.correct_answer == "4"
    assert q.options == ["3", "4", "5", "6"]


def test_question_defaults_subject_to_maths():
    q = Question(**make_question())
    assert q.subject == "maths"


def test_question_accepts_explicit_subject():
    q = Question(**make_question(subject="english"))
    assert q.subject == "english"


def test_question_rejects_unknown_subject():
    with pytest.raises(ValidationError):
        Question(**make_question(subject="science"))


def test_question_rejects_wrong_option_count():
    with pytest.raises(ValidationError):
        Question(**make_question(options=["3", "4", "5"]))


def test_question_rejects_too_many_options():
    with pytest.raises(ValidationError):
        Question(**make_question(options=["3", "4", "5", "6", "7"]))


def test_question_rejects_correct_answer_not_in_options():
    with pytest.raises(ValidationError):
        Question(**make_question(correct_answer="99"))


def test_question_rejects_unknown_topic():
    with pytest.raises(ValidationError):
        Question(**make_question(topic="division"))


def test_get_solution_request_rejects_when_nothing_provided():
    with pytest.raises(ValidationError):
        GetSolutionRequest()


def test_get_solution_request_accepts_question_id_only():
    req = GetSolutionRequest(question_id="add_sch_001")
    assert req.question_id == "add_sch_001"


def test_get_solution_request_accepts_full_trio():
    req = GetSolutionRequest(
        question_text="2 + 2 = ?",
        correct_answer="4",
        explanation_hint="2+2=4",
    )
    assert req.question_text == "2 + 2 = ?"
    assert req.correct_answer == "4"
    assert req.explanation_hint == "2+2=4"


def test_get_solution_request_rejects_partial_trio():
    with pytest.raises(ValidationError):
        GetSolutionRequest(question_text="2 + 2 = ?", correct_answer="4")


def test_get_solution_request_rejects_partial_trio_missing_text():
    with pytest.raises(ValidationError):
        GetSolutionRequest(correct_answer="4", explanation_hint="2+2=4")


def make_comprehension_question(**overrides):
    data = dict(
        id=uuid.uuid4(),
        passage_id=uuid.uuid4(),
        question_type="literal_recall",
        question_text="What did the cat do?",
        options=["Ran", "Slept", "Jumped", "Ate"],
        correct_answer="Slept",
        explanation_hint="The passage says the cat slept all day.",
    )
    data.update(overrides)
    return data


def test_comprehension_question_accepts_valid_data():
    q = ComprehensionQuestion(**make_comprehension_question())
    assert q.question_type == "literal_recall"
    assert q.correct_answer == "Slept"


def test_comprehension_question_rejects_wrong_option_count():
    with pytest.raises(ValidationError):
        ComprehensionQuestion(**make_comprehension_question(options=["Ran", "Slept"]))


def test_comprehension_question_rejects_correct_answer_not_in_options():
    with pytest.raises(ValidationError):
        ComprehensionQuestion(**make_comprehension_question(correct_answer="Flew"))


def test_comprehension_question_rejects_unknown_question_type():
    with pytest.raises(ValidationError):
        ComprehensionQuestion(**make_comprehension_question(question_type="guess_the_ending"))


def make_passage_summary(**overrides):
    data = dict(
        id=uuid.uuid4(),
        subject="english",
        title="The Sleepy Cat",
        word_count=45,
        sentence_count=8,
        difficulty_rank=3,
        created_at="2026-01-01T00:00:00Z",
    )
    data.update(overrides)
    return data


def test_passage_summary_accepts_valid_data():
    p = PassageSummary(**make_passage_summary())
    assert p.difficulty_rank == 3
    assert p.subject == "english"


@pytest.mark.parametrize("rank", [0, 51])
def test_passage_summary_rejects_difficulty_rank_out_of_range(rank):
    with pytest.raises(ValidationError):
        PassageSummary(**make_passage_summary(difficulty_rank=rank))


def make_passage_detail(**overrides):
    data = dict(
        id=uuid.uuid4(),
        subject="english",
        title="The Sleepy Cat",
        body="The cat slept all day. It did not want to play.",
        word_count=45,
        sentence_count=8,
        difficulty_rank=3,
        takeaway="Cats sleep a lot.",
        created_at="2026-01-01T00:00:00Z",
        questions=[make_comprehension_question()],
    )
    data.update(overrides)
    return data


def test_passage_detail_accepts_valid_data_with_nested_questions():
    p = PassageDetail(**make_passage_detail())
    assert len(p.questions) == 1
    assert p.questions[0].question_type == "literal_recall"


def test_passage_detail_rejects_invalid_nested_question():
    bad_question = make_comprehension_question(correct_answer="not-an-option")
    with pytest.raises(ValidationError):
        PassageDetail(**make_passage_detail(questions=[bad_question]))
