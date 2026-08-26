import uuid
import time
from datetime import datetime, timezone
from threading import Lock

import click
from flask import Flask, current_app
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded
from flask_limiter.util import get_remote_address
from sqlalchemy import delete, or_, select
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


cors = CORS()
db = SQLAlchemy()
migrate = Migrate()
jwt_manager = JWTManager()
limiter = Limiter(key_func=get_remote_address)
_cleanup_lock = Lock()


def register_extensions(app: Flask) -> None:
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    db.init_app(app)
    migrate.init_app(app, db)

    jwt_manager.init_app(app)
    limiter.init_app(app)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(error: RateLimitExceeded):
        return {"message": "Rate limit exceeded"}, 429

    @app.cli.command("cleanup-token-blocklist")
    def cleanup_token_blocklist_command() -> None:
        """Delete expired JWT revocation records."""
        deleted = cleanup_expired_tokens()
        click.echo(f"Deleted {deleted} expired token revocation record(s).")


def cleanup_expired_tokens() -> int:
    from app.models import TokenBlocklist

    result = db.session.execute(
        delete(TokenBlocklist).where(
            TokenBlocklist.expires_at <= datetime.now(timezone.utc)
        )
    )
    db.session.commit()
    return result.rowcount


def _cleanup_expired_tokens_if_due() -> None:
    now = time.monotonic()
    cleanup_after = current_app.extensions.get("token_blocklist_cleanup_after", 0)
    if now < cleanup_after or not _cleanup_lock.acquire(blocking=False):
        return

    try:
        cleanup_after = current_app.extensions.get("token_blocklist_cleanup_after", 0)
        if now < cleanup_after:
            return
        cleanup_expired_tokens()
        interval = current_app.config["TOKEN_BLOCKLIST_CLEANUP_INTERVAL"]
        current_app.extensions["token_blocklist_cleanup_after"] = now + interval
    except Exception:
        db.session.rollback()
        raise
    finally:
        _cleanup_lock.release()


@jwt_manager.token_in_blocklist_loader
def is_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    from app.models import TokenBlocklist

    _cleanup_expired_tokens_if_due()
    jti = jwt_payload["jti"]
    session_id = jwt_payload.get("sid")
    criteria = [TokenBlocklist.jti == jti]
    if session_id:
        criteria.append(TokenBlocklist.session_id == session_id)
    token = db.session.execute(
        select(TokenBlocklist.id).where(or_(*criteria))
    ).scalar_one_or_none()
    return token is not None


@jwt_manager.user_lookup_loader
def load_user(jwt_header: dict, jwt_payload: dict):
    from app.models import User

    identity = jwt_payload["sub"]
    try:
        user_id = uuid.UUID(identity)
    except ValueError:
        return None

    return db.session.get(User, user_id)
