import os

import pytest

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-with-at-least-32-bytes"
os.environ["FLASK_DEBUG"] = "false"

from app import create_app
from app.extensions import db, limiter


@pytest.fixture
def app():
    application = create_app()
    application.config.update(
        TESTING=True,
        RATELIMIT_ENABLED=True,
        TOKEN_BLOCKLIST_CLEANUP_INTERVAL=3600,
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_rate_limiter(app):
    limiter.reset()
    yield
    limiter.reset()
