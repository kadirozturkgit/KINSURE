"""Password hashing, JWT creation, and bearer-token validation helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2 before database persistence."""
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Safely compare a plaintext password with its stored Argon2 hash."""
    return password_context.verify(password, password_hash)


def create_access_token(username: str) -> str:
    """Create a signed bearer token that identifies the authenticated username."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": username, "exp": expires_at},
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed token, raising JWTError for invalid tokens."""
    return jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=["HS256"],
    )
