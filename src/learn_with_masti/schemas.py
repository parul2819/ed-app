import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

Topic = Literal["addition", "subtraction", "multiplication"]
Track = Literal["school", "olympiad"]
Difficulty = Literal["easy", "medium", "hard", "super_hard", "pro"]
SessionMode = Literal["scored", "open"]


class Question(BaseModel):
    id: str
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
    topic: Topic
    track: Track
    questions_attempted: int
    questions_correct: int
    stars_earned: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class AttemptCreateRequest(BaseModel):
    topic: Topic
    track: Track
    question_id: str = Field(min_length=1)
    selected_answer: str = Field(min_length=1)
    is_correct: bool
    mode: SessionMode = "open"
