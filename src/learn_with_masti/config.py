import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = PROJECT_ROOT / "content" / "questions"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
ANTHROPIC_MAX_TOKENS = int(os.environ.get("ANTHROPIC_MAX_TOKENS", "2048"))

# Which LLM provider to use: "anthropic" or "qwen". Defaults to "anthropic", but
# if ANTHROPIC_API_KEY isn't set, llm_client falls back to "qwen" automatically
# instead of failing.
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_TIMEOUT_SECONDS = int(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "600"))

# How many times generate_questions()/get_solution() will call the LLM before
# giving up on invalid JSON (1 initial attempt + retries).
LLM_MAX_ATTEMPTS = int(os.environ.get("LLM_MAX_ATTEMPTS", "2"))

# Stage-2 quality review of generated questions (see llm_client.review_question).
# Uses its own, typically stronger/slower models than everyday generation.
REVIEW_ENABLED = os.environ.get("REVIEW_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
ANTHROPIC_REVIEW_MODEL = os.environ.get("ANTHROPIC_REVIEW_MODEL", "claude-sonnet-4-6")
OLLAMA_REVIEW_MODEL = os.environ.get("OLLAMA_REVIEW_MODEL", "qwen3:4b")
# qwen3's reasoning ("think") mode gives better review judgments but is far
# slower on CPU-only Ollama (minutes per call, non-deterministic); disable it
# to trade some review depth for speed when that's the bottleneck.
OLLAMA_REVIEW_THINK = os.environ.get("OLLAMA_REVIEW_THINK", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://masti:masti@localhost:5432/learn_with_masti"
)

# Bounds on how long a single DB connection attempt / query is allowed to hang
# before failing with a clear error (see db.py). Postgres-only.
DB_CONNECT_TIMEOUT_SECONDS = int(os.environ.get("DB_CONNECT_TIMEOUT_SECONDS", "5"))
DB_STATEMENT_TIMEOUT_MS = int(os.environ.get("DB_STATEMENT_TIMEOUT_MS", "10000"))

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me-please-32-bytes-min")
JWT_ALGORITHM = "HS256"
PARENT_JWT_EXPIRE_MINUTES = int(os.environ.get("PARENT_JWT_EXPIRE_MINUTES", "10080"))
CHILD_JWT_EXPIRE_MINUTES = int(os.environ.get("CHILD_JWT_EXPIRE_MINUTES", "180"))
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
)

# Minimum accuracy percentage required to earn each star count.
STAR_THRESHOLD_3 = int(os.environ.get("STAR_THRESHOLD_3", "90"))
STAR_THRESHOLD_2 = int(os.environ.get("STAR_THRESHOLD_2", "70"))
STAR_THRESHOLD_1 = int(os.environ.get("STAR_THRESHOLD_1", "50"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]


def require_api_key() -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return ANTHROPIC_API_KEY
