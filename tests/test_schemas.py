import pytest
from pydantic import ValidationError

from learn_with_masti.schemas import GetSolutionRequest, Question


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
