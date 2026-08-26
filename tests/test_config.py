import pytest

from app.config import _env_bool, _env_int, _jwt_secret_key, _secret_key


def test_invalid_boolean_configuration_fails_fast(monkeypatch):
    monkeypatch.setenv("INVALID_BOOLEAN", "sometimes")

    with pytest.raises(RuntimeError, match="must be a boolean"):
        _env_bool("INVALID_BOOLEAN")


def test_invalid_integer_configuration_fails_fast(monkeypatch):
    monkeypatch.setenv("INVALID_INTEGER", "never")

    with pytest.raises(RuntimeError, match="must be an integer"):
        _env_int("INVALID_INTEGER", 1)


def test_short_production_secret_is_rejected(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "short")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    with pytest.raises(RuntimeError, match="at least 32 bytes"):
        _secret_key()


def test_short_jwt_secret_is_rejected(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "short")

    with pytest.raises(RuntimeError, match="at least 32 bytes"):
        _jwt_secret_key()
