"""One-off bulk content generation: top up each (topic, track, difficulty)
bucket in content/questions/*_full.json to TARGET questions.

Review (the slow LLM quality pass) is disabled for this run only, via an
in-process env override -- it does not touch the real .env, so the live app
still reviews questions it generates for users. Stage-1 programmatic
validation (validate_question: math correctness, digit rules, no duplicate
options) still runs on every candidate.

Usage: poetry run python scripts/bulk_generate_questions.py
"""

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("REVIEW_ENABLED", "false")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank_format import dump_bank  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from learn_with_masti import llm_client  # noqa: E402
from learn_with_masti.config import CONTENT_DIR  # noqa: E402

TOPIC_PREFIX = {"addition": "add", "subtraction": "sub", "multiplication": "mul"}
TRACK_ABBREV = {"school": "sch", "olympiad": "oly"}
BUCKETS = [
    ("school", "easy"),
    ("school", "medium"),
    ("school", "hard"),
    ("olympiad", "super_hard"),
    ("olympiad", "pro"),
]
TARGET = 30
BATCH_SIZE = 5
MAX_BATCHES_PER_BUCKET = 50


def load_bank(topic: str):
    path = CONTENT_DIR / f"{topic}_full.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def next_id_counter(questions: list[dict], prefix: str, abbrev: str) -> int:
    pattern = re.compile(rf"^{prefix}_{abbrev}_(\d+)$")
    nums = []
    for q in questions:
        m = pattern.match(q["id"])
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


async def fill_bucket(
    topic: str, track: str, difficulty: str, questions: list[dict], prefix: str, abbrev: str
) -> int:
    existing = [q for q in questions if q["track"] == track and q["difficulty"] == difficulty]
    needed = TARGET - len(existing)
    if needed <= 0:
        print(f"{topic}/{track}/{difficulty}: already has {len(existing)} >= {TARGET}, skipping")
        return 0

    print(f"{topic}/{track}/{difficulty}: need {needed} more (have {len(existing)})")
    seen_texts = {q["question_text"].strip().lower() for q in questions if q["topic"] == topic}
    counter = next_id_counter(questions, prefix, abbrev)
    recent = [q["question_text"] for q in existing][-10:]

    added = 0
    batches = 0
    while added < needed and batches < MAX_BATCHES_PER_BUCKET:
        batches += 1
        n = min(BATCH_SIZE, needed - added)
        try:
            candidates = await llm_client.generate_questions(
                topic=topic,
                track=track,
                difficulty=difficulty,
                n=n,
                recent_question_texts=recent,
            )
        except Exception as exc:  # noqa: BLE001 - keep the bulk run alive on any batch failure
            print(f"  batch {batches} failed: {exc}")
            continue

        for c in candidates:
            text_key = c.question_text.strip().lower()
            if text_key in seen_texts:
                continue
            seen_texts.add(text_key)
            new_id = f"{prefix}_{abbrev}_{counter:03d}"
            counter += 1
            questions.append(
                {
                    "id": new_id,
                    "topic": topic,
                    "track": track,
                    "difficulty": difficulty,
                    "question_text": c.question_text,
                    "options": c.options,
                    "correct_answer": c.correct_answer,
                    "explanation_hint": c.explanation_hint,
                }
            )
            recent.append(c.question_text)
            recent = recent[-10:]
            added += 1
            if added >= needed:
                break

    if added < needed:
        print(f"  WARNING: {topic}/{track}/{difficulty} only reached {added}/{needed} after {batches} batches")
    else:
        print(f"  {topic}/{track}/{difficulty}: done, added {added}")
    return added


async def main() -> None:
    for topic, prefix in TOPIC_PREFIX.items():
        path, data = load_bank(topic)
        questions = data["questions"]
        for track, difficulty in BUCKETS:
            abbrev = TRACK_ABBREV[track]
            await fill_bucket(topic, track, difficulty, questions, prefix, abbrev)
            path.write_text(dump_bank(data), encoding="utf-8")
        print(f"=== {topic} done, total questions in bank: {len(questions)} ===")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"TOTAL TIME: {time.time() - start:.1f}s")
