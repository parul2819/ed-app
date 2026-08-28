import logging
import uuid
from datetime import datetime, timedelta, timezone

import anthropic
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, llm_client
from .config import (
    CORS_ORIGINS,
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    STAR_THRESHOLD_1,
    STAR_THRESHOLD_2,
    STAR_THRESHOLD_3,
)
from .db import get_db
from .models import (
    Child,
    ChildProgress,
    ComprehensionQuestion,
    Parent,
    Passage,
    PasswordResetToken,
    PracticeSession,
    QuestionAttempt,
)
from .question_bank import find_question_by_id, get_questions, get_recent_question_texts
from .schemas import (
    AttemptCreateRequest,
    ChildCreateRequest,
    ChildPinVerifyRequest,
    ChildProgressResponse,
    ChildResponse,
    ChildSessionResponse,
    Difficulty,
    ForgotPasswordRequest,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    GetSolutionRequest,
    MessageResponse,
    ParentLoginRequest,
    ParentSignupRequest,
    PassageDetail,
    PassageProgressResponse,
    PassageSummary,
    QuestionsResponse,
    ResetPasswordRequest,
    Solution,
    Subject,
    Topic,
    Track,
    TokenResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_FORGOT_PASSWORD_GENERIC_MESSAGE = (
    "If an account with that email exists, a password reset link has been sent."
)

app = FastAPI(title="Learn with Masti API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_bearer_scheme = HTTPBearer()


def get_current_parent(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Parent:
    try:
        payload = auth.decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if payload.get("type") != "parent":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    parent = db.get(Parent, uuid.UUID(payload["sub"]))
    if parent is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return parent


def get_current_child(
    child_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Child:
    try:
        payload = auth.decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if payload.get("type") != "child":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("sub") != str(child_id):
        raise HTTPException(status_code=403, detail="Token does not match this child")

    child = db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return child


def _stars_for_accuracy(questions_correct: int, questions_attempted: int) -> int:
    if questions_attempted == 0:
        return 0
    accuracy = questions_correct / questions_attempted * 100
    if accuracy >= STAR_THRESHOLD_3:
        return 3
    if accuracy >= STAR_THRESHOLD_2:
        return 2
    if accuracy >= STAR_THRESHOLD_1:
        return 1
    return 0


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/questions", response_model=QuestionsResponse)
async def list_questions(
    topic: Topic,
    track: Track,
    difficulty: Difficulty | None = None,
    limit: int | None = None,
    subject: Subject = "maths",
) -> QuestionsResponse:
    try:
        questions = get_questions(topic, track, difficulty, limit, subject=subject)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QuestionsResponse(questions=questions)


@app.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(request: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
    if request.subject != "maths":
        raise HTTPException(
            status_code=400,
            detail=f"subject {request.subject!r} is not supported by /generate-questions; "
            "English content is served via /passages",
        )
    recent_question_texts = get_recent_question_texts(
        request.topic, request.track, request.difficulty, subject=request.subject
    )
    try:
        questions = await llm_client.generate_questions(
            topic=request.topic,
            track=request.track,
            difficulty=request.difficulty,
            n=request.n,
            recent_question_texts=recent_question_texts,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return GenerateQuestionsResponse(questions=questions)


@app.get("/passages", response_model=list[PassageSummary])
def list_passages(db: Session = Depends(get_db)) -> list[Passage]:
    return db.query(Passage).order_by(Passage.difficulty_rank).all()


@app.get("/passages/{passage_id}", response_model=PassageDetail)
def get_passage(passage_id: uuid.UUID, db: Session = Depends(get_db)) -> Passage:
    passage = db.get(Passage, passage_id)
    if passage is None:
        raise HTTPException(
            status_code=404, detail=f"No passage found with id '{passage_id}'"
        )
    return passage


@app.post("/get-solution", response_model=Solution)
async def get_solution(request: GetSolutionRequest) -> Solution:
    if request.question_id:
        question = find_question_by_id(request.question_id)
        if question is None:
            raise HTTPException(
                status_code=404,
                detail=f"No question found with id '{request.question_id}'",
            )
        question_id = question.id
        question_text = question.question_text
        correct_answer = question.correct_answer
        explanation_hint = question.explanation_hint
    else:
        question_id = "custom"
        question_text = request.question_text
        correct_answer = request.correct_answer
        explanation_hint = request.explanation_hint

    try:
        solution = await llm_client.get_solution(
            question_id=question_id,
            question_text=question_text,
            correct_answer=correct_answer,
            explanation_hint=explanation_hint,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return solution


@app.post("/parents/signup", response_model=TokenResponse, status_code=201)
def parents_signup(
    request: ParentSignupRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    parent = Parent(email=request.email, password_hash=auth.hash_secret(request.password))
    db.add(parent)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    db.refresh(parent)
    return TokenResponse(access_token=auth.create_parent_token(parent.id))


@app.post("/parents/login", response_model=TokenResponse)
def parents_login(
    request: ParentLoginRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    parent = db.query(Parent).filter(Parent.email == request.email.strip().lower()).first()
    if parent is None or not auth.verify_secret(request.password, parent.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=auth.create_parent_token(parent.id))


@app.post("/parents/forgot-password", response_model=MessageResponse)
def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    parent = db.query(Parent).filter(Parent.email == request.email.strip().lower()).first()
    if parent is not None:
        token = auth.generate_reset_token()
        reset_token = PasswordResetToken(
            parent_id=parent.id,
            token_hash=auth.hash_reset_token(token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        )
        db.add(reset_token)
        db.commit()
        # TODO: replace this with a real email service before production.
        # For now the reset token is only logged so it can be used locally in dev.
        logger.info("Password reset token for %s: %s", parent.email, token)
    return MessageResponse(message=_FORGOT_PASSWORD_GENERIC_MESSAGE)


@app.post("/parents/reset-password", response_model=MessageResponse)
def reset_password(
    request: ResetPasswordRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    token_hash = auth.hash_reset_token(request.token)
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash)
        .first()
    )

    now = datetime.now(timezone.utc)
    expires_at = reset_token.expires_at if reset_token is not None else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if reset_token is None or reset_token.used or expires_at < now:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    parent = db.get(Parent, reset_token.parent_id)
    parent.password_hash = auth.hash_secret(request.new_password)
    reset_token.used = True
    db.commit()
    return MessageResponse(message="Password has been reset. You can now log in.")


@app.post("/parents/children", response_model=ChildResponse, status_code=201)
def create_child(
    request: ChildCreateRequest,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
) -> Child:
    child = Child(
        parent_id=parent.id,
        name=request.name,
        pin_hash=auth.hash_secret(request.pin),
        grade=request.grade,
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@app.get("/parents/children", response_model=list[ChildResponse])
def list_children(
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
) -> list[Child]:
    return (
        db.query(Child)
        .filter(Child.parent_id == parent.id)
        .order_by(Child.created_at)
        .all()
    )


@app.post("/children/{child_id}/verify-pin", response_model=ChildSessionResponse)
def verify_child_pin(
    child_id: uuid.UUID,
    request: ChildPinVerifyRequest,
    db: Session = Depends(get_db),
) -> ChildSessionResponse:
    child = db.get(Child, child_id)
    if child is None or not auth.verify_secret(request.pin, child.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid child or PIN")
    return ChildSessionResponse(
        access_token=auth.create_child_session_token(child.id),
        child_id=child.id,
        name=child.name,
    )


@app.get("/children/{child_id}/progress", response_model=list[ChildProgressResponse])
def get_child_progress(
    child_id: uuid.UUID,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[ChildProgress]:
    return db.query(ChildProgress).filter(ChildProgress.child_id == child_id).all()


@app.get(
    "/children/{child_id}/passage-progress", response_model=list[PassageProgressResponse]
)
def get_child_passage_progress(
    child_id: uuid.UUID,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[PassageProgressResponse]:
    attempts = (
        db.query(QuestionAttempt)
        .join(PracticeSession, PracticeSession.id == QuestionAttempt.session_id)
        .filter(
            PracticeSession.child_id == child_id,
            PracticeSession.subject == "english",
        )
        .all()
    )
    if not attempts:
        return []

    # question_attempts.question_id is a plain string column (shared with the
    # maths bank's string ids), not a foreign key -- so it's matched to
    # comprehension_questions.id in Python rather than a SQL join, which
    # sidesteps having to cast a UUID column to text identically across
    # Postgres (prod) and SQLite (tests).
    question_to_passage = {
        str(question.id): passage
        for question, passage in db.query(ComprehensionQuestion, Passage).join(
            Passage, Passage.id == ComprehensionQuestion.passage_id
        )
    }

    stats: dict[uuid.UUID, dict] = {}
    for attempt in attempts:
        passage = question_to_passage.get(attempt.question_id)
        if passage is None:
            continue
        entry = stats.setdefault(
            passage.id,
            {
                "passage": passage,
                "questions_attempted": 0,
                "questions_correct": 0,
                "last_attempted_at": attempt.answered_at,
            },
        )
        entry["questions_attempted"] += 1
        if attempt.is_correct:
            entry["questions_correct"] += 1
        if attempt.answered_at > entry["last_attempted_at"]:
            entry["last_attempted_at"] = attempt.answered_at

    results = [
        PassageProgressResponse(
            passage_id=entry["passage"].id,
            title=entry["passage"].title,
            difficulty_rank=entry["passage"].difficulty_rank,
            questions_attempted=entry["questions_attempted"],
            questions_correct=entry["questions_correct"],
            stars_earned=_stars_for_accuracy(
                entry["questions_correct"], entry["questions_attempted"]
            ),
            last_attempted_at=entry["last_attempted_at"],
        )
        for entry in stats.values()
    ]
    results.sort(key=lambda r: r.last_attempted_at, reverse=True)
    return results


@app.post("/children/{child_id}/attempts", response_model=ChildProgressResponse, status_code=201)
def record_attempt(
    child_id: uuid.UUID,
    request: AttemptCreateRequest,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> ChildProgress:
    session = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.child_id == child_id,
            PracticeSession.subject == request.subject,
            PracticeSession.topic == request.topic,
            PracticeSession.track == request.track,
            PracticeSession.mode == request.mode,
            PracticeSession.completed_at.is_(None),
        )
        .order_by(PracticeSession.started_at.desc())
        .first()
    )
    if session is None:
        session = PracticeSession(
            child_id=child_id,
            subject=request.subject,
            topic=request.topic,
            track=request.track,
            mode=request.mode,
        )
        db.add(session)
        db.flush()

    attempt = QuestionAttempt(
        session_id=session.id,
        question_id=request.question_id,
        selected_answer=request.selected_answer,
        is_correct=request.is_correct,
    )
    db.add(attempt)

    progress = db.get(ChildProgress, (child_id, request.subject, request.topic, request.track))
    if progress is None:
        progress = ChildProgress(
            child_id=child_id,
            subject=request.subject,
            topic=request.topic,
            track=request.track,
            questions_attempted=0,
            questions_correct=0,
            stars_earned=0,
        )
        db.add(progress)

    progress.questions_attempted += 1
    if request.is_correct:
        progress.questions_correct += 1
    progress.stars_earned = _stars_for_accuracy(
        progress.questions_correct, progress.questions_attempted
    )

    db.commit()
    db.refresh(progress)
    return progress
