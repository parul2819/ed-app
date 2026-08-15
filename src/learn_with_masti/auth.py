import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from .config import CHILD_JWT_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET, PARENT_JWT_EXPIRE_MINUTES

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_secret(secret: str) -> str:
    return _pwd_context.hash(secret)


def verify_secret(secret: str, secret_hash: str) -> bool:
    return _pwd_context.verify(secret, secret_hash)


def _create_token(subject: uuid.UUID, token_type: str, expire_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_parent_token(parent_id: uuid.UUID) -> str:
    return _create_token(parent_id, "parent", PARENT_JWT_EXPIRE_MINUTES)


def create_child_session_token(child_id: uuid.UUID) -> str:
    return _create_token(child_id, "child", CHILD_JWT_EXPIRE_MINUTES)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    # A deterministic hash (not bcrypt) so the plaintext token sent to the
    # user can be looked up by hash; safe here since the token itself is a
    # high-entropy random value, not a user-chosen secret.
    return hashlib.sha256(token.encode()).hexdigest()
