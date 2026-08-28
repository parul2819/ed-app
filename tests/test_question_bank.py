import pytest

from learn_with_masti import question_bank


def test_get_recent_question_texts_matches_track_and_difficulty():
    all_qs = question_bank._load_topic_questions("addition")
    expected = [
        q["question_text"]
        for q in all_qs
        if q["track"] == "school" and q["difficulty"] == "easy"
    ]
    assert expected, "fixture assumption: addition has school/easy questions"

    texts = question_bank.get_recent_question_texts("addition", "school", "easy")
    assert texts == expected[-10:]


def test_get_recent_question_texts_respects_limit():
    texts = question_bank.get_recent_question_texts(
        "addition", "school", "medium", limit=2
    )
    assert len(texts) <= 2


def test_get_recent_question_texts_falls_back_when_no_exact_match():
    all_qs = question_bank._load_topic_questions("addition")
    # Fixture assumption: the olympiad track has no "easy" difficulty questions.
    assert not any(
        q["track"] == "olympiad" and q["difficulty"] == "easy" for q in all_qs
    )

    texts = question_bank.get_recent_question_texts("addition", "olympiad", "easy")

    expected = [q["question_text"] for q in all_qs if q["track"] == "olympiad"]
    assert texts == expected[-10:]
    assert len(texts) > 0


def test_get_questions_filters_by_topic_and_track():
    all_qs = question_bank._load_topic_questions("addition")
    expected_ids = {q["id"] for q in all_qs if q["track"] == "school"}

    results = question_bank.get_questions("addition", "school")

    assert {q.id for q in results} == expected_ids
    assert all(q.topic == "addition" and q.track == "school" for q in results)


def test_get_questions_filters_by_difficulty_when_given():
    all_qs = question_bank._load_topic_questions("addition")
    expected_ids = {
        q["id"] for q in all_qs if q["track"] == "school" and q["difficulty"] == "easy"
    }
    assert expected_ids, "fixture assumption: addition has school/easy questions"

    results = question_bank.get_questions("addition", "school", difficulty="easy")

    assert {q.id for q in results} == expected_ids
    assert all(q.difficulty == "easy" for q in results)


def test_get_questions_respects_limit():
    results = question_bank.get_questions("addition", "school", limit=2)
    assert len(results) <= 2


def test_get_questions_returns_validated_question_objects():
    results = question_bank.get_questions("addition", "school", limit=1)
    assert len(results) == 1
    assert isinstance(results[0], question_bank.Question)


def test_get_questions_returns_empty_list_when_no_match():
    results = question_bank.get_questions("addition", "olympiad", difficulty="easy")
    assert results == []


def test_find_question_by_id_found_in_each_topic():
    for question_id, expected_topic, expected_track in [
        ("add_sch_001", "addition", "school"),
        ("sub_oly_001", "subtraction", "olympiad"),
        ("mul_sch_005", "multiplication", "school"),
    ]:
        q = question_bank.find_question_by_id(question_id)
        assert q is not None
        assert q.id == question_id
        assert q.topic == expected_topic
        assert q.track == expected_track


def test_find_question_by_id_returns_none_for_unknown_id():
    assert question_bank.find_question_by_id("does_not_exist_123") is None


def test_get_questions_defaults_subject_to_maths():
    results = question_bank.get_questions("addition", "school", limit=1)
    assert results[0].subject == "maths"


def test_get_questions_rejects_non_maths_subject():
    with pytest.raises(ValueError, match="not served by the question bank"):
        question_bank.get_questions("addition", "school", subject="english")


def test_get_recent_question_texts_rejects_non_maths_subject():
    with pytest.raises(ValueError, match="not served by the question bank"):
        question_bank.get_recent_question_texts(
            "addition", "school", "easy", subject="english"
        )


def test_find_question_by_id_rejects_non_maths_subject():
    with pytest.raises(ValueError, match="not served by the question bank"):
        question_bank.find_question_by_id("add_sch_001", subject="english")
