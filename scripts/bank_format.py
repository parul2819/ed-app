"""Shared JSON formatting for content/questions/*_full.json.

Keeps the hand-authored style (2-space indent, "options" arrays inline)
instead of the fully-expanded output json.dumps(indent=2) would produce, so
diffs against hand-written entries stay small.
"""

import json


def _s(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def format_question(q: dict) -> str:
    options = ", ".join(_s(o) for o in q["options"])
    return (
        "    {\n"
        f'      "id": {_s(q["id"])},\n'
        f'      "topic": {_s(q["topic"])},\n'
        f'      "track": {_s(q["track"])},\n'
        f'      "difficulty": {_s(q["difficulty"])},\n'
        f'      "question_text": {_s(q["question_text"])},\n'
        f"      \"options\": [{options}],\n"
        f'      "correct_answer": {_s(q["correct_answer"])},\n'
        f'      "explanation_hint": {_s(q["explanation_hint"])}\n'
        "    }"
    )


def dump_bank(data: dict) -> str:
    questions_text = ",\n".join(format_question(q) for q in data["questions"])
    notes_line = f'  "notes": {_s(data["notes"])},\n' if "notes" in data else ""
    return (
        "{\n"
        f'  "topic": {_s(data["topic"])},\n'
        f"{notes_line}"
        '  "questions": [\n'
        f"{questions_text}\n"
        "  ]\n"
        "}\n"
    )
