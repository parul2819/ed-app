import json
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

import learn_with_masti.llm_client as llm_client
from learn_with_masti.main import app

VALID_QUESTION_JSON = json.dumps(
    {
        "id": "addition_school_gen_1234",
        "topic": "addition",
        "track": "school",
        "difficulty": "easy",
        "question_text": "40 + 20 = ?",
        "options": ["58", "59", "60", "61"],
        "correct_answer": "60",
        "explanation_hint": "40 + 20 = 60.",
    }
)

VALID_SOLUTION_JSON = json.dumps(
    {
        "steps": ["Step 1: Add the numbers.", "Step 2: 40 + 20 = 60."],
        "final_answer": "60",
        "encouragement": "Great job!",
    }
)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _sequenced_fake_provider(responses):
    responses = iter(responses)

    async def fake_complete(system_prompt, user_prompt):
        return next(responses)

    provider = SimpleNamespace(complete=fake_complete)
    return lambda: provider


def _reviewer_must_not_be_called():
    async def fake_complete(system_prompt, user_prompt):
        raise AssertionError("reviewer should not have been called")

    return lambda: SimpleNamespace(complete=fake_complete)


WRONG_ARITHMETIC_QUESTION_JSON = json.dumps(
    {
        "id": "addition_school_gen_bad",
        "topic": "addition",
        "track": "school",
        "difficulty": "easy",
        "question_text": "40 + 20 = ?",
        "options": ["58", "59", "60", "61"],
        "correct_answer": "59",
        "explanation_hint": "wrong on purpose",
    }
)

SECOND_VALID_QUESTION_JSON = json.dumps(
    {
        "id": "addition_school_gen_5678",
        "topic": "addition",
        "track": "school",
        "difficulty": "easy",
        "question_text": "10 + 15 = ?",
        "options": ["23", "24", "25", "26"],
        "correct_answer": "25",
        "explanation_hint": "10 + 15 = 25.",
    }
)


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_get_questions_returns_bank_questions_for_topic_and_track(client):
    resp = await client.get(
        "/questions", params={"topic": "addition", "track": "school"}
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) > 0
    assert all(
        q["topic"] == "addition" and q["track"] == "school" for q in data["questions"]
    )


async def test_get_questions_filters_by_difficulty(client):
    resp = await client.get(
        "/questions",
        params={"topic": "addition", "track": "school", "difficulty": "easy"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) > 0
    assert all(q["difficulty"] == "easy" for q in data["questions"])


async def test_get_questions_respects_limit(client):
    resp = await client.get(
        "/questions",
        params={"topic": "addition", "track": "school", "limit": 2},
    )

    assert resp.status_code == 200
    assert len(resp.json()["questions"]) <= 2


async def test_get_questions_invalid_topic_returns_422(client):
    resp = await client.get(
        "/questions", params={"topic": "geometry", "track": "school"}
    )

    assert resp.status_code == 422


async def test_get_questions_defaults_subject_to_maths(client):
    resp = await client.get(
        "/questions", params={"topic": "addition", "track": "school"}
    )

    assert resp.status_code == 200
    assert all(q["subject"] == "maths" for q in resp.json()["questions"])


async def test_get_questions_rejects_english_subject_with_400(client):
    resp = await client.get(
        "/questions",
        params={"topic": "addition", "track": "school", "subject": "english"},
    )

    assert resp.status_code == 400


async def test_generate_questions_rejects_english_subject_with_400(client):
    resp = await client.post(
        "/generate-questions",
        json={
            "subject": "english",
            "topic": "addition",
            "track": "school",
            "difficulty": "easy",
            "n": 1,
        },
    )

    assert resp.status_code == 400


async def test_generate_questions_valid_response_parses(client, monkeypatch):
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider([VALID_QUESTION_JSON])
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) == 1
    assert data["questions"][0]["id"] == "addition_school_gen_1234"
    assert data["questions"][0]["correct_answer"] == "60"


async def test_generate_questions_invalid_then_valid_retries_and_succeeds(
    client, monkeypatch
):
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider(["not valid json", VALID_QUESTION_JSON]),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 200
    assert resp.json()["questions"][0]["correct_answer"] == "60"


async def test_generate_questions_invalid_twice_returns_502(client, monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider(["still not json", "still not json either"]),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 502


async def test_generate_questions_respects_configured_max_attempts(client, monkeypatch):
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)
    monkeypatch.setattr(llm_client, "LLM_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider(["nope", "still nope", VALID_QUESTION_JSON]),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 200
    assert resp.json()["questions"][0]["correct_answer"] == "60"


async def test_generate_questions_gives_up_after_configured_max_attempts(
    client, monkeypatch
):
    monkeypatch.setattr(llm_client, "LLM_MAX_ATTEMPTS", 1)
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider(["not valid json"])
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 502


async def test_generate_questions_handles_concatenated_json_objects(
    client, monkeypatch
):
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)
    second_question = json.dumps(
        {
            "id": "addition_school_gen_5678",
            "topic": "addition",
            "track": "school",
            "difficulty": "easy",
            "question_text": "10 + 15 = ?",
            "options": ["23", "24", "25", "26"],
            "correct_answer": "25",
            "explanation_hint": "10 + 15 = 25.",
        }
    )
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider([f"{VALID_QUESTION_JSON}\n{second_question}"]),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 2},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) == 2
    assert data["questions"][0]["correct_answer"] == "60"
    assert data["questions"][1]["correct_answer"] == "25"


async def test_generate_questions_discards_candidate_failing_stage1_validation(
    client, monkeypatch
):
    monkeypatch.setattr(llm_client, "LLM_MAX_ATTEMPTS", 1)
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider([WRONG_ARITHMETIC_QUESTION_JSON])
    )
    # Reviewer must never be reached — stage 1 should discard this first.
    monkeypatch.setattr(llm_client, "get_review_provider", _reviewer_must_not_be_called())

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 502


async def test_generate_questions_skips_reviewer_when_review_disabled(client, monkeypatch):
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider([VALID_QUESTION_JSON])
    )
    # If REVIEW_ENABLED weren't actually honored, this would blow up instead
    # of a clean 200.
    monkeypatch.setattr(llm_client, "get_review_provider", _reviewer_must_not_be_called())

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 200
    assert resp.json()["questions"][0]["correct_answer"] == "60"


async def test_generate_questions_accepts_candidate_approved_by_reviewer(client, monkeypatch):
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider([VALID_QUESTION_JSON])
    )
    monkeypatch.setattr(
        llm_client,
        "get_review_provider",
        _sequenced_fake_provider([json.dumps({"approved": True, "problems": []})]),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 200
    assert resp.json()["questions"][0]["correct_answer"] == "60"


async def test_generate_questions_retries_when_reviewer_rejects_candidate(
    client, monkeypatch
):
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider([VALID_QUESTION_JSON, SECOND_VALID_QUESTION_JSON]),
    )
    monkeypatch.setattr(
        llm_client,
        "get_review_provider",
        _sequenced_fake_provider(
            [
                json.dumps({"approved": False, "problems": ["distractors too close"]}),
                json.dumps({"approved": True, "problems": []}),
            ]
        ),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 1},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) == 1
    assert data["questions"][0]["correct_answer"] == "25"


async def test_generate_questions_returns_partial_results_after_max_attempts(
    client, monkeypatch
):
    monkeypatch.setattr(llm_client, "LLM_MAX_ATTEMPTS", 1)
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider([VALID_QUESTION_JSON])
    )
    monkeypatch.setattr(
        llm_client,
        "get_review_provider",
        _sequenced_fake_provider([json.dumps({"approved": True, "problems": []})]),
    )

    resp = await client.post(
        "/generate-questions",
        json={"topic": "addition", "track": "school", "difficulty": "easy", "n": 2},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) == 1
    assert data["questions"][0]["correct_answer"] == "60"


async def test_get_solution_valid_response_parses(client, monkeypatch):
    monkeypatch.setattr(
        llm_client, "get_provider", _sequenced_fake_provider([VALID_SOLUTION_JSON])
    )

    resp = await client.post("/get-solution", json={"question_id": "add_sch_003"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["question_id"] == "add_sch_003"
    assert data["final_answer"] == "60"
    assert data["steps"] == [
        "Step 1: Add the numbers.",
        "Step 2: 40 + 20 = 60.",
    ]


async def test_get_solution_invalid_then_valid_retries_and_succeeds(
    client, monkeypatch
):
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider(["nope not json", VALID_SOLUTION_JSON]),
    )

    resp = await client.post("/get-solution", json={"question_id": "add_sch_003"})

    assert resp.status_code == 200
    assert resp.json()["final_answer"] == "60"


async def test_get_solution_invalid_twice_returns_502(client, monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "get_provider",
        _sequenced_fake_provider(["garbage", "still garbage"]),
    )

    resp = await client.post("/get-solution", json={"question_id": "add_sch_003"})

    assert resp.status_code == 502


async def test_get_solution_unknown_question_id_returns_404(client):
    resp = await client.post(
        "/get-solution", json={"question_id": "does_not_exist_123"}
    )

    assert resp.status_code == 404
