import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"{name} environment variable is required")
    return value


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _env_csv(name: str, default: str = "*") -> str | list[str]:
    value = os.getenv(name, default)
    if value == "*":
        return value
    return [item.strip() for item in value.split(",") if item.strip()]


def _jwt_secret_key() -> str:
    value = os.getenv("JWT_SECRET_KEY")
    if value:
        return value

    secret_key = os.getenv("SECRET_KEY")
    if secret_key and len(secret_key.encode()) >= 32:
        return secret_key

    if _env_bool("FLASK_DEBUG"):
        return "dev-jwt-secret-key-change-me-for-local-use-only"

    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is required unless SECRET_KEY is at "
        "least 32 bytes"
    )


class Config:
    DEBUG = _env_bool("FLASK_DEBUG")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-for-local-use-only")
    JWT_SECRET_KEY = _jwt_secret_key()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    CORS_ORIGINS = _env_csv("CORS_ORIGINS")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _required_env("DATABASE_URL")
