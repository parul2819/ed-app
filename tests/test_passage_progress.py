from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from learn_with_masti.db import Base, get_db
from learn_with_masti.main import app
from learn_with_masti.models import ComprehensionQuestion, Passage, QuestionAttempt


@pytest.fixture
async def db_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    yield TestSessionLocal

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
async def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def _signup_and_login(client, email="parent@example.com", password="hunter22"):
    await client.post("/parents/signup", json={"email": email, "password": password})
    resp = await client.post("/parents/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


async def _add_child(client, parent_token, name="Rohan", pin="1234"):
    resp = await client.post(
        "/parents/children",
        json={"name": name, "pin": pin, "grade": 3},
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    return resp.json()["id"]


async def _create_and_login_child(
    client, parent_email="parent@example.com", name="Rohan", pin="1234"
):
    parent_token = await _signup_and_login(client, email=parent_email)
    child_id = await _add_child(client, parent_token, name=name, pin=pin)
    resp = await client.post(f"/children/{child_id}/verify-pin", json={"pin": pin})
    return child_id, resp.json()["access_token"]


def _make_passage(db, *, title, difficulty_rank, num_questions=2):
    passage = Passage(
        subject="english",
        title=title,
        body="Sample passage body text used only for progress endpoint tests.",
        word_count=45,
        sentence_count=8,
        difficulty_rank=difficulty_rank,
        takeaway="A short lesson.",
    )
    db.add(passage)
    db.flush()

    questions = []
    for i in range(num_questions):
        question = ComprehensionQuestion(
            passage_id=passage.id,
            question_type="literal_recall",
            question_text=f"Question {i}?",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            explanation_hint="Hint.",
        )
        db.add(question)
        questions.append(question)

    db.commit()
    db.refresh(passage)
    for question in questions:
        db.refresh(question)
    return passage, questions


async def _record_attempt(client, child_id, headers, question_id, is_correct):
    return await client.post(
        f"/children/{child_id}/attempts",
        json={
            "subject": "english",
            "topic": "comprehension",
            "track": "school",
            "question_id": question_id,
            "selected_answer": "A" if is_correct else "B",
            "is_correct": is_correct,
        },
        headers=headers,
    )


async def test_get_passage_progress_returns_empty_list_initially(client):
    child_id, child_token = await _create_and_login_child(client)

    resp = await client.get(
        f"/children/{child_id}/passage-progress",
        headers={"Authorization": f"Bearer {child_token}"},
    )

    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_passage_progress_requires_child_token(client):
    child_id, _ = await _create_and_login_child(client)

    resp = await client.get(f"/children/{child_id}/passage-progress")

    assert resp.status_code in (401, 403)


async def test_get_passage_progress_rejects_mismatched_child_token(client):
    child_a_id, _ = await _create_and_login_child(
        client, parent_email="parenta@example.com", name="ChildA", pin="1111"
    )
    _, child_b_token = await _create_and_login_child(
        client, parent_email="parentb@example.com", name="ChildB", pin="2222"
    )

    resp = await client.get(
        f"/children/{child_a_id}/passage-progress",
        headers={"Authorization": f"Bearer {child_b_token}"},
    )

    assert resp.status_code == 403


async def test_get_passage_progress_aggregates_attempts_for_one_passage(
    client, db_session_factory
):
    child_id, child_token = await _create_and_login_child(client)
    headers = {"Authorization": f"Bearer {child_token}"}

    db = db_session_factory()
    try:
        passage, questions = _make_passage(
            db, title="A Passage", difficulty_rank=5, num_questions=2
        )
        passage_id = str(passage.id)
        q1_id, q2_id = (str(q.id) for q in questions)
    finally:
        db.close()

    await _record_attempt(client, child_id, headers, q1_id, is_correct=True)
    await _record_attempt(client, child_id, headers, q2_id, is_correct=False)

    resp = await client.get(f"/children/{child_id}/passage-progress", headers=headers)

    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    row = rows[0]
    assert row["passage_id"] == passage_id
    assert row["title"] == "A Passage"
    assert row["difficulty_rank"] == 5
    assert row["questions_attempted"] == 2
    assert row["questions_correct"] == 1
    assert row["stars_earned"] == 1  # 50% accuracy meets the default 1-star threshold
    assert row["last_attempted_at"]


async def test_get_passage_progress_counts_retries_cumulatively(client, db_session_factory):
    child_id, child_token = await _create_and_login_child(client)
    headers = {"Authorization": f"Bearer {child_token}"}

    db = db_session_factory()
    try:
        _, questions = _make_passage(
            db, title="Retry Passage", difficulty_rank=3, num_questions=1
        )
        (question_id,) = (str(q.id) for q in questions)
    finally:
        db.close()

    await _record_attempt(client, child_id, headers, question_id, is_correct=True)
    await _record_attempt(client, child_id, headers, question_id, is_correct=True)

    resp = await client.get(f"/children/{child_id}/passage-progress", headers=headers)

    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["questions_attempted"] == 2
    assert rows[0]["questions_correct"] == 2
    assert rows[0]["stars_earned"] == 3


async def test_get_passage_progress_orders_by_most_recent_attempt(client, db_session_factory):
    child_id, child_token = await _create_and_login_child(client)
    headers = {"Authorization": f"Bearer {child_token}"}

    db = db_session_factory()
    try:
        _, older_questions = _make_passage(
            db, title="Older Passage", difficulty_rank=2, num_questions=1
        )
        _, newer_questions = _make_passage(
            db, title="Newer Passage", difficulty_rank=8, num_questions=1
        )
        (older_question_id,) = (str(q.id) for q in older_questions)
        (newer_question_id,) = (str(q.id) for q in newer_questions)
    finally:
        db.close()

    await _record_attempt(client, child_id, headers, older_question_id, is_correct=True)
    await _record_attempt(client, child_id, headers, newer_question_id, is_correct=True)

    # The two attempts above can land in the same second under SQLite's
    # timestamp resolution, which would make the ordering assertion flaky --
    # so pin the timestamps explicitly to guarantee a real time difference.
    db = db_session_factory()
    try:
        older_attempt = (
            db.query(QuestionAttempt)
            .filter(QuestionAttempt.question_id == older_question_id)
            .one()
        )
        newer_attempt = (
            db.query(QuestionAttempt)
            .filter(QuestionAttempt.question_id == newer_question_id)
            .one()
        )
        older_attempt.answered_at = datetime.now(timezone.utc) - timedelta(hours=1)
        newer_attempt.answered_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    resp = await client.get(f"/children/{child_id}/passage-progress", headers=headers)

    titles = [row["title"] for row in resp.json()]
    assert titles == ["Newer Passage", "Older Passage"]


async def test_get_passage_progress_ignores_maths_attempts(client, db_session_factory):
    child_id, child_token = await _create_and_login_child(client)
    headers = {"Authorization": f"Bearer {child_token}"}

    await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
        },
        headers=headers,
    )

    resp = await client.get(f"/children/{child_id}/passage-progress", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == []
