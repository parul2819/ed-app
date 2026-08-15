# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Planning docs live in `docs/PROJECT_NOTES_backup.md` (product spec: vision, MVP scope, content format, build sequence) and `docs/llm_prompts.md` (design notes and rationale for the LLM question-generation and step-wise-solution prompts). The actual prompt text is the `prompts/` directory at the project root (`question_generation_system.txt`, `question_generation_user.txt`, `solution_system.txt`, `solution_user.txt`) — `src/learn_with_masti/llm_client.py` loads these files at import time. To change prompt wording, edit the files under `prompts/` directly; `docs/llm_prompts.md` is documentation, not the source.

Python 3.12+ project managed with Poetry (`pyproject.toml`, src layout under `src/learn_with_masti/`). The stray top-level `venv/` directory predates Poetry's own managed virtualenv and is unused — always use `poetry install` / `poetry run`, not that directory.

### Commands

```
poetry install                                          # install dependencies
poetry run uvicorn learn_with_masti.main:app --reload    # run the dev server (http://127.0.0.1:8000)
poetry run pytest                                        # run the test suite
poetry run pytest tests/test_main.py -k retries -v       # run a single test file / matching tests
```

Tests mock the LLM call (`learn_with_masti.llm_client.get_provider`) via `monkeypatch`, so no API key or network access is needed to run them; `question_bank` tests read the real `content/questions/*_full.json` files.

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` before calling `/generate-questions` or `/get-solution` — both hit the Anthropic API. `.env` is gitignored.

### Architecture

- `src/learn_with_masti/main.py` — FastAPI app with three endpoints: `GET /health`, `POST /generate-questions`, `POST /get-solution`.
- `src/learn_with_masti/schemas.py` — Pydantic models for requests/responses, including the `Question` schema shared with the JSON question-bank files (options must be length-4 and contain `correct_answer`).
- `src/learn_with_masti/question_bank.py` — loads and caches `content/questions/{topic}_full.json`; supplies recent question texts (for LLM de-duplication context) and looks up a question by `id` for `/get-solution`.
- `src/learn_with_masti/llm_client.py` — loads the system/user prompts from `prompts/` at import time, selects an LLM provider (`AnthropicProvider` or `QwenProvider`, see `get_provider()`), strips markdown code fences, and validates the JSON response against the Pydantic schema — retrying up to `LLM_MAX_ATTEMPTS` times on invalid JSON/schema before raising.
- `src/learn_with_masti/config.py` — loads `.env` via `python-dotenv`; env vars override defaults for the LLM model/provider, retry/timeout tuning, and star thresholds.
- `content/questions/*_full.json` — the seed question banks (`{topic}_full.json`, 15 school + 10 olympiad questions each); `*_samples.json` are earlier style references, not loaded by the app.
- `prompts/*.txt` — the actual LLM prompt text (question generation + step-wise solution, system + user each); source of truth, see `docs/llm_prompts.md` for design rationale.

## Product summary

EdTech app for school students, starting with **Class 3, Math only** (Addition, Subtraction, Multiplication — single-digit). Two tracks: School Syllabus and Olympiad (SOF/IMO) prep. Questions are MCQ (4 options) stored as JSON with fields: `id`, `topic`, `track`, `difficulty`, `question_text`, `options`, `correct_answer`, `explanation_hint`.

Two LLM-powered features are planned: generating fresh practice questions when the bank runs low, and generating step-wise, Class-3-appropriate solutions on wrong answers. Progress tracking uses accuracy/stars/badges, deliberately not a competitive leaderboard.

Build order is content/backend first, gamified UI (balloon-pop game, timer mode, mascot) last — see `docs/PROJECT_NOTES_backup.md`'s Build Sequence for the intended order of work.
