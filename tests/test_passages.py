import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from learn_with_masti.db import Base, get_db
from learn_with_masti.main import app
from learn_with_masti.models import ComprehensionQuestion, Passage


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


def _make_passage(db, *, title, difficulty_rank, with_question=True):
    passage = Passage(
        subject="english",
        title=title,
        body="The cat sat on the mat. It was a sunny day.",
        word_count=45,
        sentence_count=8,
        difficulty_rank=difficulty_rank,
        takeaway="Cats like sunny days.",
    )
    db.add(passage)
    db.flush()

    if with_question:
        question = ComprehensionQuestion(
            passage_id=passage.id,
            question_type="literal_recall",
            question_text="Where did the cat sit?",
            options=["On the mat", "On the bed", "On the roof", "On the chair"],
            correct_answer="On the mat",
            explanation_hint="The passage says the cat sat on the mat.",
        )
        db.add(question)

    db.commit()
    db.refresh(passage)
    return passage


async def test_list_passages_returns_empty_list_initially(client):
    resp = await client.get("/passages")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_passages_orders_by_difficulty_rank(client, db_session_factory):
    db = db_session_factory()
    try:
        _make_passage(db, title="Hardest", difficulty_rank=40)
        _make_passage(db, title="Easiest", difficulty_rank=2)
        _make_passage(db, title="Middle", difficulty_rank=20)
    finally:
        db.close()

    resp = await client.get("/passages")

    assert resp.status_code == 200
    titles = [p["title"] for p in resp.json()]
    assert titles == ["Easiest", "Middle", "Hardest"]


async def test_list_passages_summary_omits_body_and_questions(client, db_session_factory):
    db = db_session_factory()
    try:
        _make_passage(db, title="A Passage", difficulty_rank=5)
    finally:
        db.close()

    resp = await client.get("/passages")

    assert resp.status_code == 200
    passage = resp.json()[0]
    assert "body" not in passage
    assert "questions" not in passage
    assert passage["word_count"] == 45


async def test_get_passage_returns_detail_with_questions(client, db_session_factory):
    db = db_session_factory()
    try:
        passage = _make_passage(db, title="A Passage", difficulty_rank=5)
        passage_id = passage.id
    finally:
        db.close()

    resp = await client.get(f"/passages/{passage_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "A Passage"
    assert data["takeaway"] == "Cats like sunny days."
    assert len(data["questions"]) == 1
    assert data["questions"][0]["question_type"] == "literal_recall"
    assert data["questions"][0]["correct_answer"] == "On the mat"


async def test_get_passage_returns_404_for_unknown_id(client):
    resp = await client.get(f"/passages/{uuid.uuid4()}")

    assert resp.status_code == 404
