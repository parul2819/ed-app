import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import learn_with_masti.auth as auth
import learn_with_masti.main as main
from learn_with_masti.db import Base, get_db
from learn_with_masti.main import app
from learn_with_masti.models import PracticeSession


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


async def _signup(client, email="parent@example.com", password="hunter22"):
    return await client.post(
        "/parents/signup", json={"email": email, "password": password}
    )


async def _signup_and_login(client, email="parent@example.com", password="hunter22"):
    await _signup(client, email, password)
    resp = await client.post(
        "/parents/login", json={"email": email, "password": password}
    )
    return resp.json()["access_token"]


async def _add_child(client, parent_token, name="Rohan", pin="1234", grade=3):
    resp = await client.post(
        "/parents/children",
        json={"name": name, "pin": pin, "grade": grade},
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


async def test_parent_signup_returns_token(client):
    resp = await _signup(client)

    assert resp.status_code == 201
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


async def test_parent_signup_rejects_short_password(client):
    resp = await _signup(client, password="short")

    assert resp.status_code == 422


async def test_parent_signup_duplicate_email_returns_409(client):
    await _signup(client, email="dup@example.com")
    resp = await _signup(client, email="dup@example.com")

    assert resp.status_code == 409


async def test_parent_login_succeeds_with_correct_credentials(client):
    await _signup(client, email="login@example.com", password="correcthorse")

    resp = await client.post(
        "/parents/login",
        json={"email": "login@example.com", "password": "correcthorse"},
    )

    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_parent_login_rejects_wrong_password(client):
    await _signup(client, email="login2@example.com", password="correcthorse")

    resp = await client.post(
        "/parents/login",
        json={"email": "login2@example.com", "password": "wrongpassword"},
    )

    assert resp.status_code == 401


async def test_parent_login_rejects_unknown_email(client):
    resp = await client.post(
        "/parents/login",
        json={"email": "nobody@example.com", "password": "whatever1"},
    )

    assert resp.status_code == 401


async def test_forgot_password_returns_generic_message_for_unknown_email(client):
    resp = await client.post(
        "/parents/forgot-password", json={"email": "nobody@example.com"}
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == (
        "If an account with that email exists, a password reset link has been sent."
    )


async def test_forgot_password_returns_same_generic_message_for_known_email(client):
    await _signup(client, email="reset@example.com")

    resp = await client.post(
        "/parents/forgot-password", json={"email": "reset@example.com"}
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == (
        "If an account with that email exists, a password reset link has been sent."
    )


async def test_reset_password_succeeds_with_valid_token(client, monkeypatch):
    monkeypatch.setattr(auth, "generate_reset_token", lambda: "fixed-reset-token")
    await _signup(client, email="reset2@example.com", password="oldpassword1")
    await client.post("/parents/forgot-password", json={"email": "reset2@example.com"})

    resp = await client.post(
        "/parents/reset-password",
        json={"token": "fixed-reset-token", "new_password": "newpassword1"},
    )

    assert resp.status_code == 200

    new_login = await client.post(
        "/parents/login",
        json={"email": "reset2@example.com", "password": "newpassword1"},
    )
    assert new_login.status_code == 200

    old_login = await client.post(
        "/parents/login",
        json={"email": "reset2@example.com", "password": "oldpassword1"},
    )
    assert old_login.status_code == 401


async def test_reset_password_rejects_unknown_token(client):
    resp = await client.post(
        "/parents/reset-password",
        json={"token": "not-a-real-token", "new_password": "newpassword1"},
    )

    assert resp.status_code == 400


async def test_reset_password_rejects_already_used_token(client, monkeypatch):
    monkeypatch.setattr(auth, "generate_reset_token", lambda: "reuse-token")
    await _signup(client, email="reset3@example.com", password="oldpassword1")
    await client.post("/parents/forgot-password", json={"email": "reset3@example.com"})

    first = await client.post(
        "/parents/reset-password",
        json={"token": "reuse-token", "new_password": "newpassword1"},
    )
    assert first.status_code == 200

    second = await client.post(
        "/parents/reset-password",
        json={"token": "reuse-token", "new_password": "anotherpassword1"},
    )
    assert second.status_code == 400


async def test_reset_password_rejects_expired_token(client, monkeypatch):
    monkeypatch.setattr(main, "PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", -5)
    monkeypatch.setattr(auth, "generate_reset_token", lambda: "expired-token")
    await _signup(client, email="reset4@example.com", password="oldpassword1")
    await client.post("/parents/forgot-password", json={"email": "reset4@example.com"})

    resp = await client.post(
        "/parents/reset-password",
        json={"token": "expired-token", "new_password": "newpassword1"},
    )

    assert resp.status_code == 400


async def test_reset_password_rejects_short_new_password(client, monkeypatch):
    monkeypatch.setattr(auth, "generate_reset_token", lambda: "short-pw-token")
    await _signup(client, email="reset5@example.com", password="oldpassword1")
    await client.post("/parents/forgot-password", json={"email": "reset5@example.com"})

    resp = await client.post(
        "/parents/reset-password",
        json={"token": "short-pw-token", "new_password": "short"},
    )

    assert resp.status_code == 422


async def test_create_child_requires_parent_token(client):
    resp = await client.post(
        "/parents/children", json={"name": "Rohan", "pin": "1234"}
    )

    assert resp.status_code in (401, 403)


async def test_create_child_rejects_invalid_token(client):
    resp = await client.post(
        "/parents/children",
        json={"name": "Rohan", "pin": "1234"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert resp.status_code == 401


async def test_create_child_succeeds_with_parent_token(client):
    token = await _signup_and_login(client)

    resp = await client.post(
        "/parents/children",
        json={"name": "Rohan", "pin": "1234", "grade": 3},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Rohan"
    assert data["grade"] == 3
    assert "pin" not in data
    assert "pin_hash" not in data


async def test_create_child_rejects_non_numeric_pin(client):
    token = await _signup_and_login(client)

    resp = await client.post(
        "/parents/children",
        json={"name": "Rohan", "pin": "abcd"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 422


async def test_verify_child_pin_succeeds(client):
    token = await _signup_and_login(client)
    create_resp = await client.post(
        "/parents/children",
        json={"name": "Meera", "pin": "4321"},
        headers={"Authorization": f"Bearer {token}"},
    )
    child_id = create_resp.json()["id"]

    resp = await client.post(f"/children/{child_id}/verify-pin", json={"pin": "4321"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["child_id"] == child_id
    assert data["name"] == "Meera"
    assert data["access_token"]


async def test_verify_child_pin_rejects_wrong_pin(client):
    token = await _signup_and_login(client)
    create_resp = await client.post(
        "/parents/children",
        json={"name": "Meera", "pin": "4321"},
        headers={"Authorization": f"Bearer {token}"},
    )
    child_id = create_resp.json()["id"]

    resp = await client.post(f"/children/{child_id}/verify-pin", json={"pin": "0000"})

    assert resp.status_code == 401


async def test_verify_child_pin_rejects_unknown_child(client):
    resp = await client.post(
        "/children/00000000-0000-0000-0000-000000000000/verify-pin",
        json={"pin": "1234"},
    )

    assert resp.status_code == 401


async def test_list_children_requires_parent_token(client):
    resp = await client.get("/parents/children")

    assert resp.status_code in (401, 403)


async def test_list_children_returns_empty_list_initially(client):
    token = await _signup_and_login(client)

    resp = await client.get(
        "/parents/children", headers={"Authorization": f"Bearer {token}"}
    )

    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_children_returns_created_children(client):
    token = await _signup_and_login(client)
    await _add_child(client, token, name="Rohan", pin="1234")
    await _add_child(client, token, name="Meera", pin="4321")

    resp = await client.get(
        "/parents/children", headers={"Authorization": f"Bearer {token}"}
    )

    assert resp.status_code == 200
    names = {child["name"] for child in resp.json()}
    assert names == {"Rohan", "Meera"}


async def test_list_children_only_returns_own_children(client):
    token_a = await _signup_and_login(client, email="parenta@example.com")
    await _add_child(client, token_a, name="ChildA", pin="1234")
    token_b = await _signup_and_login(client, email="parentb@example.com")
    await _add_child(client, token_b, name="ChildB", pin="5678")

    resp = await client.get(
        "/parents/children", headers={"Authorization": f"Bearer {token_a}"}
    )

    assert resp.status_code == 200
    names = {child["name"] for child in resp.json()}
    assert names == {"ChildA"}


async def test_get_progress_requires_child_token(client):
    child_id, _ = await _create_and_login_child(client)

    resp = await client.get(f"/children/{child_id}/progress")

    assert resp.status_code in (401, 403)


async def test_get_progress_rejects_mismatched_child_token(client):
    child_a_id, _ = await _create_and_login_child(
        client, parent_email="parenta@example.com", name="ChildA", pin="1111"
    )
    _, child_b_token = await _create_and_login_child(
        client, parent_email="parentb@example.com", name="ChildB", pin="2222"
    )

    resp = await client.get(
        f"/children/{child_a_id}/progress",
        headers={"Authorization": f"Bearer {child_b_token}"},
    )

    assert resp.status_code == 403


async def test_get_progress_returns_empty_list_initially(client):
    child_id, child_token = await _create_and_login_child(client)

    resp = await client.get(
        f"/children/{child_id}/progress",
        headers={"Authorization": f"Bearer {child_token}"},
    )

    assert resp.status_code == 200
    assert resp.json() == []


async def test_record_attempt_star_thresholds_are_configurable(client, monkeypatch):
    # Default STAR_THRESHOLD_1 is 50, so 50% accuracy earns 1 star (see
    # test_record_attempt_increments_existing_progress). Raise the bar and
    # confirm the same 50% accuracy now earns 0 stars.
    monkeypatch.setattr(main, "STAR_THRESHOLD_1", 60)
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
    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_002",
            "selected_answer": "99",
            "is_correct": False,
        },
        headers=headers,
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["questions_attempted"] == 2
    assert data["questions_correct"] == 1
    assert data["stars_earned"] == 0


async def test_record_attempt_defaults_mode_to_open(
    client, db_session_factory
):
    child_id, child_token = await _create_and_login_child(client)

    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
        },
        headers={"Authorization": f"Bearer {child_token}"},
    )

    assert resp.status_code == 201
    db = db_session_factory()
    try:
        session = db.query(PracticeSession).filter(
            PracticeSession.child_id == uuid.UUID(child_id)
        ).one()
        assert session.mode == "open"
    finally:
        db.close()


async def test_record_attempt_accepts_scored_mode(client, db_session_factory):
    child_id, child_token = await _create_and_login_child(client)

    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
            "mode": "scored",
        },
        headers={"Authorization": f"Bearer {child_token}"},
    )

    assert resp.status_code == 201
    db = db_session_factory()
    try:
        session = db.query(PracticeSession).filter(
            PracticeSession.child_id == uuid.UUID(child_id)
        ).one()
        assert session.mode == "scored"
    finally:
        db.close()


async def test_record_attempt_rejects_invalid_mode(client):
    child_id, child_token = await _create_and_login_child(client)

    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
            "mode": "bogus",
        },
        headers={"Authorization": f"Bearer {child_token}"},
    )

    assert resp.status_code == 422


async def test_record_attempt_different_modes_create_separate_sessions(
    client, db_session_factory
):
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
            "mode": "open",
        },
        headers=headers,
    )
    await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_002",
            "selected_answer": "5",
            "is_correct": True,
            "mode": "scored",
        },
        headers=headers,
    )

    db = db_session_factory()
    try:
        sessions = (
            db.query(PracticeSession)
            .filter(PracticeSession.child_id == uuid.UUID(child_id))
            .order_by(PracticeSession.started_at)
            .all()
        )
        assert [s.mode for s in sessions] == ["open", "scored"]
    finally:
        db.close()


async def test_record_attempt_creates_progress_row(client):
    child_id, child_token = await _create_and_login_child(client)

    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
        },
        headers={"Authorization": f"Bearer {child_token}"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["child_id"] == child_id
    assert data["topic"] == "addition"
    assert data["track"] == "school"
    assert data["questions_attempted"] == 1
    assert data["questions_correct"] == 1
    assert data["stars_earned"] == 3


async def test_record_attempt_increments_existing_progress(client):
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
    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_002",
            "selected_answer": "99",
            "is_correct": False,
        },
        headers=headers,
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["questions_attempted"] == 2
    assert data["questions_correct"] == 1
    assert data["stars_earned"] == 1  # 50% accuracy


async def test_record_attempt_tracks_topics_separately(client):
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
    await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "subtraction",
            "track": "school",
            "question_id": "sub_sch_001",
            "selected_answer": "1",
            "is_correct": True,
        },
        headers=headers,
    )

    resp = await client.get(f"/children/{child_id}/progress", headers=headers)

    assert resp.status_code == 200
    topics = {row["topic"] for row in resp.json()}
    assert topics == {"addition", "subtraction"}


async def test_record_attempt_rejects_mismatched_child_token(client):
    child_a_id, _ = await _create_and_login_child(
        client, parent_email="parenta@example.com", name="ChildA", pin="1111"
    )
    _, child_b_token = await _create_and_login_child(
        client, parent_email="parentb@example.com", name="ChildB", pin="2222"
    )

    resp = await client.post(
        f"/children/{child_a_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
        },
        headers={"Authorization": f"Bearer {child_b_token}"},
    )

    assert resp.status_code == 403


async def test_record_attempt_requires_child_token(client):
    child_id, _ = await _create_and_login_child(client)

    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
        },
    )

    assert resp.status_code in (401, 403)


async def test_record_attempt_rejects_parent_token(client):
    parent_token = await _signup_and_login(client)
    child_id = await _add_child(client, parent_token, name="Rohan", pin="1234")

    resp = await client.post(
        f"/children/{child_id}/attempts",
        json={
            "topic": "addition",
            "track": "school",
            "question_id": "add_sch_001",
            "selected_answer": "4",
            "is_correct": True,
        },
        headers={"Authorization": f"Bearer {parent_token}"},
    )

    assert resp.status_code == 401
