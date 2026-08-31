import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .reading_levels import MAX_RANK, MIN_RANK, QuestionType

Subject = Literal["maths", "english"]
# "comprehension" is the sole topic for subject="english" (passages aren't split
# by topic); attempts on passage questions always use track="school" since there
# is no olympiad reading track. Keep these two values consistent across
# PassagePage.jsx, ProgressPage.jsx, and scripts/seed_english_passages.py.
Topic = Literal["addition", "subtraction", "multiplication", "division", "comprehension"]
Track = Literal["school", "olympiad"]
Difficulty = Literal["easy", "medium", "hard", "super_hard", "pro"]
SessionMode = Literal["scored", "open"]


class Question(BaseModel):
    id: str
    subject: Subject = "maths"
    topic: Topic
    track: Track
    difficulty: Difficulty
    question_text: str
    options: list[str]
    correct_answer: str
    explanation_hint: str

    @model_validator(mode="after")
    def _check_answer_in_options(self) -> "Question":
        if len(self.options) != 4:
            raise ValueError("options must contain exactly 4 choices")
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of options")
        return self


class GenerateQuestionsRequest(BaseModel):
    subject: Subject = "maths"
    topic: Topic
    track: Track
    difficulty: Difficulty
    n: int = Field(default=1, ge=1, le=10)


class GenerateQuestionsResponse(BaseModel):
    questions: list[Question]


class QuestionsResponse(BaseModel):
    questions: list[Question]


class GetSolutionRequest(BaseModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation_hint: Optional[str] = None

    @model_validator(mode="after")
    def _check_lookup_fields(self) -> "GetSolutionRequest":
        if self.question_id:
            return self
        if self.question_text and self.correct_answer and self.explanation_hint:
            return self
        raise ValueError(
            "Provide either question_id, or question_text + correct_answer + explanation_hint"
        )


class Solution(BaseModel):
    question_id: str
    steps: list[str]
    final_answer: str
    encouragement: str


class QuestionReview(BaseModel):
    approved: bool
    problems: list[str] = []


class ParentSignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or " " in value:
            raise ValueError("email must be a valid email address")
        return value


class ParentLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class MessageResponse(BaseModel):
    message: str


class ChildCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    pin: str = Field(min_length=4, max_length=6)
    grade: int = Field(default=3, ge=1, le=12)

    @field_validator("pin")
    @classmethod
    def _pin_must_be_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("pin must contain only digits")
        return value


class ChildResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID
    name: str
    grade: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChildPinVerifyRequest(BaseModel):
    pin: str


class ChildSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    child_id: uuid.UUID
    name: str


class ChildProgressResponse(BaseModel):
    child_id: uuid.UUID
    subject: Subject
    topic: Topic
    track: Track
    questions_attempted: int
    questions_correct: int
    stars_earned: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class AttemptCreateRequest(BaseModel):
    subject: Subject = "maths"
    topic: Topic
    track: Track
    question_id: str = Field(min_length=1)
    selected_answer: str = Field(min_length=1)
    is_correct: bool
    mode: SessionMode = "open"
    difficulty: Optional[Difficulty] = None
    # True for the first attempt of a fresh practice round (a new level visit,
    # or a passage retry) -- starts a new PracticeSession instead of folding
    # into whichever one this child/topic/track last used, so attempt-history
    # can report separate scores per round instead of one running total.
    new_session: bool = False


class AttemptRoundResponse(BaseModel):
    """One practice round (one PracticeSession) with its own score, for the
    attempt-history report -- as opposed to ChildProgressResponse/
    PassageProgressResponse, which aggregate every round together."""

    session_id: uuid.UUID
    subject: Subject
    topic: Topic
    track: Track
    difficulty: Optional[Difficulty] = None
    passage_id: Optional[uuid.UUID] = None
    passage_title: Optional[str] = None
    passage_difficulty_rank: Optional[int] = None
    questions_attempted: int
    questions_correct: int
    stars_earned: int
    started_at: datetime

    model_config = {"from_attributes": True}


class ComprehensionQuestion(BaseModel):
    id: uuid.UUID
    passage_id: uuid.UUID
    question_type: QuestionType
    question_text: str
    options: list[str]
    correct_answer: str
    explanation_hint: str

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def _check_answer_in_options(self) -> "ComprehensionQuestion":
        if len(self.options) != 4:
            raise ValueError("options must contain exactly 4 choices")
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of options")
        return self


class PassageSummary(BaseModel):
    """Lightweight shape for listing passages (no body/questions)."""

    id: uuid.UUID
    subject: Subject
    title: str
    word_count: int
    sentence_count: int
    difficulty_rank: int = Field(ge=MIN_RANK, le=MAX_RANK)
    created_at: datetime

    model_config = {"from_attributes": True}


class PassageProgressResponse(BaseModel):
    """One row per passage a child has attempted, aggregated across every
    attempt on that passage's questions (including retries)."""

    passage_id: uuid.UUID
    title: str
    difficulty_rank: int = Field(ge=MIN_RANK, le=MAX_RANK)
    questions_attempted: int
    questions_correct: int
    stars_earned: int
    last_attempted_at: datetime

    model_config = {"from_attributes": True}


class PassageDetail(BaseModel):
    id: uuid.UUID
    subject: Subject
    title: str
    body: str
    word_count: int
    sentence_count: int
    difficulty_rank: int = Field(ge=MIN_RANK, le=MAX_RANK)
    takeaway: str
    created_at: datetime
    questions: list[ComprehensionQuestion]

    model_config = {"from_attributes": True}
