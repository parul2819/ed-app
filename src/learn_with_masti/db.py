from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATABASE_URL, DB_CONNECT_TIMEOUT_SECONDS, DB_STATEMENT_TIMEOUT_MS

def _build_connect_args(database_url: str) -> dict[str, object]:
    # Without these, a stuck/unreachable Postgres (e.g. the connection blackholed
    # by a stale WSL/Podman port-forward, or a lock held by another session) hangs
    # a request forever with no error: psycopg has no default connect timeout, and
    # Postgres has no default statement timeout. Bound both so a genuinely broken
    # DB fails fast with a clear error instead of hanging indefinitely.
    if database_url.startswith("postgresql"):
        return {
            "connect_timeout": DB_CONNECT_TIMEOUT_SECONDS,
            "options": f"-c statement_timeout={DB_STATEMENT_TIMEOUT_MS}",
        }
    return {}


engine = create_engine(DATABASE_URL, connect_args=_build_connect_args(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
