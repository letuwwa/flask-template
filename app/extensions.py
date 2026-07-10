import uuid

from flask import Flask
from sqlalchemy import select
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


cors = CORS()
db = SQLAlchemy()
migrate = Migrate()
jwt_manager = JWTManager()


def register_extensions(app: Flask) -> None:
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    db.init_app(app)
    migrate.init_app(app, db)

    jwt_manager.init_app(app)


@jwt_manager.token_in_blocklist_loader
def is_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    from app.models import TokenBlocklist

    jti = jwt_payload["jti"]
    token = db.session.execute(
        select(TokenBlocklist.id).where(TokenBlocklist.jti == jti)
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
