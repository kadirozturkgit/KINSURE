"""Application settings loaded from environment variables and the local .env file."""

import secrets
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def create_ephemeral_jwt_secret() -> SecretStr:
    """Provide an unpredictable development secret when none is configured."""
    return SecretStr(secrets.token_urlsafe(32))


class Settings(BaseSettings):
    """Typed runtime configuration for the API, Oracle pool, and authentication."""

    database_user: str = ""
    database_password: SecretStr = SecretStr("")
    database_dsn: str = ""
    database_pool_min: int = Field(default=1, ge=1)
    database_pool_max: int = Field(default=5, ge=1)
    database_pool_increment: int = Field(default=1, ge=1)
    jwt_secret_key: SecretStr = Field(default_factory=create_ephemeral_jwt_secret)
    access_token_expire_minutes: int = Field(default=60, gt=0)
    log_directory: Path = Path(r"C:\Kadir\KINSURE\logs")
    allowed_origins: list[str] = ["http://localhost:4200"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
