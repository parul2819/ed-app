import json
from functools import lru_cache

from .config import CONTENT_DIR
from .schemas import Difficulty, Question, Subject, Topic, Track

TOPIC_FILES = {
    "addition": "addition_full.json",
    "subtraction": "subtraction_full.json",
    "multiplication": "multiplication_full.json",
}


def _require_maths(subject: Subject) -> None:
    """The JSON question banks only ever hold "maths" content -- English
    content lives in the passages/comprehension_questions DB tables instead
    (see main.py's /passages endpoints). Raise clearly rather than silently
    returning nothing for any other subject."""
    if subject != "maths":
        raise ValueError(
            f"subject {subject!r} is not served by the question bank; "
            "English content is served via /passages"
        )


@lru_cache(maxsize=None)
def _load_topic_questions(topic: Topic) -> tuple[dict, ...]:
    path = CONTENT_DIR / TOPIC_FILES[topic]
    if not path.exists():
        raise FileNotFoundError(f"No question bank file found for topic '{topic}' at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(data["questions"])


def get_questions(
    topic: Topic,
    track: Track,
    difficulty: Difficulty | None = None,
    limit: int | None = None,
    subject: Subject = "maths",
) -> list[Question]:
    _require_maths(subject)
    questions = _load_topic_questions(topic)
    matching = [
        Question.model_validate(q)
        for q in questions
        if q["track"] == track and (difficulty is None or q["difficulty"] == difficulty)
    ]
    if limit is not None:
        matching = matching[:limit]
    return matching


def get_recent_question_texts(
    topic: Topic, track: Track, difficulty: Difficulty, limit: int = 10, subject: Subject = "maths"
) -> list[str]:
    _require_maths(subject)
    questions = _load_topic_questions(topic)
    matching = [
        q["question_text"]
        for q in questions
        if q["track"] == track and q["difficulty"] == difficulty
    ]
    if not matching:
        matching = [q["question_text"] for q in questions if q["track"] == track]
    return matching[-limit:]


def find_question_by_id(question_id: str, subject: Subject = "maths") -> Question | None:
    _require_maths(subject)
    for topic in TOPIC_FILES:
        for q in _load_topic_questions(topic):
            if q["id"] == question_id:
                return Question.model_validate(q)
    return None
