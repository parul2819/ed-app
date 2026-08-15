import json
from functools import lru_cache

from .config import CONTENT_DIR
from .schemas import Difficulty, Question, Topic, Track

TOPIC_FILES = {
    "addition": "addition_full.json",
    "subtraction": "subtraction_full.json",
    "multiplication": "multiplication_full.json",
}


@lru_cache(maxsize=None)
def _load_topic_questions(topic: Topic) -> tuple[dict, ...]:
    path = CONTENT_DIR / TOPIC_FILES[topic]
    if not path.exists():
        raise FileNotFoundError(f"No question bank file found for topic '{topic}' at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(data["questions"])


def get_questions(
    topic: Topic, track: Track, difficulty: Difficulty | None = None, limit: int | None = None
) -> list[Question]:
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
    topic: Topic, track: Track, difficulty: Difficulty, limit: int = 10
) -> list[str]:
    questions = _load_topic_questions(topic)
    matching = [
        q["question_text"]
        for q in questions
        if q["track"] == track and q["difficulty"] == difficulty
    ]
    if not matching:
        matching = [q["question_text"] for q in questions if q["track"] == track]
    return matching[-limit:]


def find_question_by_id(question_id: str) -> Question | None:
    for topic in TOPIC_FILES:
        for q in _load_topic_questions(topic):
            if q["id"] == question_id:
                return Question.model_validate(q)
    return None
