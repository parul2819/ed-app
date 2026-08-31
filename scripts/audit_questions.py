"""Audit content/questions/*_full.json for LLM-generated mistakes.

Runs the programmatic checks in learn_with_masti.validation (arithmetic
correctness, single-correct-option, hint/answer agreement, topic digit
rules, duplicate options, operation-matches-topic, duplicate question_text)
over every question in a bank file and prints a per-question report plus
summary counts. Read-only: it never modifies or deletes anything.

Usage:
    poetry run python scripts/audit_questions.py                # all three seed banks
    poetry run python scripts/audit_questions.py content/questions/addition_full.json
    poetry run python scripts/audit_questions.py --review        # also run stage-2 LLM review
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pydantic import ValidationError  # noqa: E402

from learn_with_masti.config import CONTENT_DIR  # noqa: E402
from learn_with_masti.llm_client import review_question  # noqa: E402
from learn_with_masti.schemas import Question  # noqa: E402
from learn_with_masti.validation import validate_bank  # noqa: E402

DEFAULT_FILES = [
    CONTENT_DIR / "addition_full.json",
    CONTENT_DIR / "subtraction_full.json",
    CONTENT_DIR / "multiplication_full.json",
    CONTENT_DIR / "division_full.json",
]


async def _review_all(questions: list[Question]) -> dict[str, list[str]]:
    """Run stage-2 LLM review on every question, returning id -> problems for
    the ones the reviewer rejects (or couldn't be reached for)."""
    problems_by_id: dict[str, list[str]] = {}
    for q in questions:
        try:
            review = await review_question(q)
        except Exception as exc:  # noqa: BLE001 - report any reviewer failure, keep auditing
            detail = str(exc) or repr(exc)
            problems_by_id[q.id] = [f"reviewer call failed: {type(exc).__name__}: {detail}"]
            continue
        if not review.approved:
            problems_by_id[q.id] = [f"reviewer: {p}" for p in review.problems]
    return problems_by_id


def audit_file(path: Path, review: bool = False) -> tuple[int, int]:
    """Print a report for one bank file. Returns (total, flagged) counts."""
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_questions = data["questions"]

    questions: list[Question] = []
    problems_by_id: dict[str, list[str]] = {}
    for raw in raw_questions:
        qid = raw.get("id", "<no id>")
        try:
            questions.append(Question.model_validate(raw))
        except ValidationError as exc:
            problems_by_id.setdefault(qid, []).extend(
                f"schema: {err['msg']} (at {'.'.join(str(p) for p in err['loc'])})"
                for err in exc.errors()
            )

    for qid, problems in validate_bank(questions).items():
        problems_by_id.setdefault(qid, []).extend(problems)

    if review:
        # Only send questions that already passed stage 1 to the (slow,
        # costly) LLM reviewer -- stage 1 failures are reported already.
        stage1_failed_ids = set(problems_by_id)
        survivors = [q for q in questions if q.id not in stage1_failed_ids]
        review_problems = asyncio.run(_review_all(survivors))
        for qid, problems in review_problems.items():
            problems_by_id.setdefault(qid, []).extend(problems)

    print(f"\n=== {path.name} ({len(raw_questions)} questions) ===")
    flagged = 0
    for raw in raw_questions:
        qid = raw.get("id", "<no id>")
        problems = problems_by_id.get(qid)
        if not problems:
            continue
        flagged += 1
        print(f"\n[{qid}] {raw.get('topic')}/{raw.get('track')}/{raw.get('difficulty')}")
        print(f"  Q: {raw.get('question_text')}")
        print(f"  options: {raw.get('options')}  correct_answer: {raw.get('correct_answer')!r}")
        print(f"  hint: {raw.get('explanation_hint')}")
        for p in problems:
            print(f"  - {p}")

    total = len(raw_questions)
    print(f"\n{path.name}: {total - flagged}/{total} clean, {flagged} flagged")
    return total, flagged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Bank JSON files to audit (default: all three seed banks)")
    parser.add_argument(
        "--review",
        action="store_true",
        help="Also run stage-2 LLM review (see llm_client.review_question) on questions that pass stage 1",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in args.files] or DEFAULT_FILES
    grand_total = 0
    grand_flagged = 0
    for path in paths:
        total, flagged = audit_file(path, review=args.review)
        grand_total += total
        grand_flagged += flagged

    print(f"\n=== SUMMARY: {grand_total - grand_flagged}/{grand_total} clean, "
          f"{grand_flagged} flagged across {len(paths)} file(s) ===")


if __name__ == "__main__":
    main()
