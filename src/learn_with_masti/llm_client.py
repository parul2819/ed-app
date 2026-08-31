import json
import logging
import re
from typing import Any, Protocol

import anthropic
import httpx
from anthropic import AsyncAnthropic
from pydantic import ValidationError

from .config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MAX_TOKENS,
    ANTHROPIC_MODEL,
    ANTHROPIC_REVIEW_MODEL,
    LLM_MAX_ATTEMPTS,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_REVIEW_MODEL,
    OLLAMA_REVIEW_THINK,
    OLLAMA_TIMEOUT_SECONDS,
    PROMPTS_DIR,
    REVIEW_ENABLED,
    require_api_key,
)
from .schemas import Question, QuestionReview, Solution
from .validation import validate_question

logger = logging.getLogger(__name__)


class Provider(Protocol):
    async def complete(self, system_prompt: str, user_prompt: str) -> str: ...


class AnthropicProvider:
    def __init__(self, model: str | None = None) -> None:
        self._model = model
        self._client: AsyncAnthropic | None = None

    def _get_client(self) -> AsyncAnthropic:
        if self._client is None:
            self._client = AsyncAnthropic(api_key=require_api_key())
        return self._client

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        client = self._get_client()
        response = await client.messages.create(
            model=self._model or ANTHROPIC_MODEL,
            max_tokens=ANTHROPIC_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


_LEADING_THINK_BLOCK_RE = re.compile(r"^\s*<think>.*?</think>\s*", re.DOTALL)


def _strip_think_block(text: str) -> str:
    return _LEADING_THINK_BLOCK_RE.sub("", text, count=1)


class QwenProvider:
    def __init__(self, model: str | None = None, think: bool = False) -> None:
        self._model = model
        self._think = think

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        async with httpx.AsyncClient(
            base_url=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT_SECONDS
        ) as client:
            response = await client.post(
                "/api/chat",
                json={
                    "model": self._model or OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    # qwen3's reasoning mode adds a slow <think>...</think>
                    # preamble; skip it for everyday generation but keep it
                    # on for review (self._think), where quality > speed.
                    "think": self._think,
                },
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
            return _strip_think_block(content)


_anthropic_provider = AnthropicProvider()
_qwen_provider = QwenProvider()
_anthropic_review_provider = AnthropicProvider(model=ANTHROPIC_REVIEW_MODEL)
_qwen_review_provider = QwenProvider(model=OLLAMA_REVIEW_MODEL, think=OLLAMA_REVIEW_THINK)


def get_provider() -> Provider:
    provider_name = LLM_PROVIDER
    if provider_name == "anthropic" and not ANTHROPIC_API_KEY:
        provider_name = "qwen"
    if provider_name == "qwen":
        return _qwen_provider
    return _anthropic_provider


def get_review_provider() -> Provider:
    provider_name = LLM_PROVIDER
    if provider_name == "anthropic" and not ANTHROPIC_API_KEY:
        provider_name = "qwen"
    if provider_name == "qwen":
        return _qwen_review_provider
    return _anthropic_review_provider


# Prompts are loaded from prompts/ (see docs/llm_prompts.md, which documents
# them but is no longer the source of truth — prompts/ is).


def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Prompt file not found: {path}. Expected prompt files under {PROMPTS_DIR}."
        )
    return path.read_text(encoding="utf-8").rstrip("\n")


QUESTION_GENERATION_SYSTEM_PROMPT = _load_prompt("question_generation_system.txt")
QUESTION_GENERATION_USER_TEMPLATE = _load_prompt("question_generation_user.txt")
SOLUTION_SYSTEM_PROMPT = _load_prompt("solution_system.txt")
SOLUTION_USER_TEMPLATE = _load_prompt("solution_user.txt")
QUESTION_REVIEW_SYSTEM_PROMPT = _load_prompt("question_review_system.txt")
QUESTION_REVIEW_USER_TEMPLATE = _load_prompt("question_review_user.txt")


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return match.group(1) if match else text


def _parse_concatenated_json_values(text: str) -> list[Any]:
    """Extract every top-level JSON value from text, in order.

    Handles LLMs that emit multiple back-to-back JSON objects (e.g. one per
    question) instead of wrapping them in a single array, which json.loads
    rejects with "Extra data".
    """
    decoder = json.JSONDecoder()
    values: list[Any] = []
    idx = 0
    length = len(text)
    while idx < length:
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break
        value, idx = decoder.raw_decode(text, idx)
        values.append(value)

    if not values:
        raise json.JSONDecodeError("Expecting value", text, 0)
    return values


def _parse_json(raw_text: str) -> Any:
    text = _strip_code_fences(_strip_think_block(raw_text))
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _parse_concatenated_json_values(text)


async def review_question(question: Question) -> QuestionReview:
    user_prompt = QUESTION_REVIEW_USER_TEMPLATE.format(
        topic=question.topic,
        track=question.track,
        difficulty=question.difficulty,
        question_text=question.question_text,
        options=question.options,
        correct_answer=question.correct_answer,
        explanation_hint=question.explanation_hint,
    )
    provider = get_review_provider()
    raw_text = await provider.complete(QUESTION_REVIEW_SYSTEM_PROMPT, user_prompt)
    parsed = _parse_json(raw_text)
    if isinstance(parsed, list):
        parsed = parsed[0] if parsed else {}
    return QuestionReview.model_validate(parsed)


async def _passes_quality_checks(candidate: Question) -> bool:
    """Run stage-1 programmatic validation, then stage-2 LLM review.

    Logs the reason and returns False the moment either stage rejects the
    candidate, so callers can just discard it and move on.
    """
    problems = validate_question(candidate)
    if problems:
        logger.info(
            "Discarding generated question %s: failed validation: %s",
            candidate.id,
            "; ".join(problems),
        )
        return False

    if not REVIEW_ENABLED:
        return True

    try:
        review = await review_question(candidate)
    except (
        json.JSONDecodeError,
        ValidationError,
        TypeError,
        httpx.HTTPError,
        anthropic.APIError,
    ) as exc:
        logger.info(
            "Discarding generated question %s: reviewer call failed: %s",
            candidate.id,
            exc,
        )
        return False

    if not review.approved:
        logger.info(
            "Discarding generated question %s: reviewer rejected: %s",
            candidate.id,
            "; ".join(review.problems),
        )
        return False

    return True


async def _generate_and_filter_candidates(
    provider: Provider, user_prompt: str
) -> tuple[list[Question], Exception | None]:
    """Run one generation call, then stage-1+2 filtering on what came back.

    Returns (approved_candidates, parse_error) — parse_error is set (and the
    candidate list empty) only when the LLM's response wasn't valid question
    JSON at all.
    """
    raw_text = await provider.complete(QUESTION_GENERATION_SYSTEM_PROMPT, user_prompt)
    try:
        parsed = _parse_json(raw_text)
        items = parsed if isinstance(parsed, list) else [parsed]
        candidates = [Question.model_validate(item) for item in items]
    except (json.JSONDecodeError, ValidationError, TypeError) as exc:
        return [], exc

    return [c for c in candidates if await _passes_quality_checks(c)], None


async def generate_questions(
    topic: str,
    track: str,
    difficulty: str,
    n: int,
    recent_question_texts: list[str],
) -> list[Question]:
    user_prompt = QUESTION_GENERATION_USER_TEMPLATE.format(
        n=n,
        topic=topic,
        track=track,
        difficulty=difficulty,
        recent_question_texts=(
            "\n".join(f"- {text}" for text in recent_question_texts) or "(none)"
        ),
    )

    provider = get_provider()
    approved: list[Question] = []
    last_error: Exception | None = None

    for _attempt in range(LLM_MAX_ATTEMPTS):
        kept, error = await _generate_and_filter_candidates(provider, user_prompt)
        if error is not None:
            last_error = error
            continue

        approved.extend(kept)
        if len(approved) >= n:
            return approved[:n]

    if approved:
        return approved
    if last_error is not None:
        raise ValueError(f"LLM did not return valid question JSON after retry: {last_error}")
    raise ValueError("No generated questions passed validation/review after retry")


async def get_solution(
    question_id: str,
    question_text: str,
    correct_answer: str,
    explanation_hint: str,
) -> Solution:
    user_prompt = SOLUTION_USER_TEMPLATE.format(
        question_text=question_text,
        correct_answer=correct_answer,
        explanation_hint=explanation_hint,
    )

    provider = get_provider()
    last_error: Exception | None = None
    for _attempt in range(LLM_MAX_ATTEMPTS):
        raw_text = await provider.complete(SOLUTION_SYSTEM_PROMPT, user_prompt)
        try:
            parsed = _parse_json(raw_text)
            if not isinstance(parsed, dict):
                raise TypeError("Expected a JSON object for the solution")
            parsed["question_id"] = question_id
            return Solution.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            last_error = exc
            continue

    raise ValueError(f"LLM did not return valid solution JSON after retry: {last_error}")
