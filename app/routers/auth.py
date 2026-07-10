import re
from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    jwt_required,
)
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import TokenBlocklist, User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


@auth_bp.route("", strict_slashes=False)
def index():
    return {"status": "ok"}, 200


@auth_bp.post("/register", strict_slashes=False)
def register():
    data = _json_body()
    errors = _validate_register_payload(data)
    if errors:
        return {"errors": errors}, 400

    email = data["email"].strip().lower()
    username = data["username"].strip().lower()

    existing_user = db.session.execute(
        select(User).where(or_(User.email == email, User.username == username))
    ).scalar_one_or_none()
    if existing_user is not None:
        return {"message": "Email or username is already registered"}, 409

    user = User(
        email=email,
        username=username,
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        is_active=True,
    )
    user.set_password(data["password"])

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Email or username is already registered"}, 409

    return {"user": user.to_dict(), "tokens": _create_token_pair(user)}, 201


@auth_bp.post("/login", strict_slashes=False)
def login():
    data = _json_body()
    identifier = _login_identifier(data)
    password = _string_value(data, "password")

    if not identifier or not password:
        return {"message": "Invalid credentials"}, 401

    user = db.session.execute(
        select(User).where(or_(User.email == identifier, User.username == identifier))
    ).scalar_one_or_none()
    if user is None or not user.check_password(password):
        return {"message": "Invalid credentials"}, 401

    if not user.is_active:
        return {"message": "User account is disabled"}, 403

    return {"user": user.to_dict(), "tokens": _create_token_pair(user)}, 200


@auth_bp.post("/refresh", strict_slashes=False)
@jwt_required(refresh=True)
def refresh():
    if current_user is None:
        return {"message": "User not found"}, 401

    if not current_user.is_active:
        return {"message": "User account is disabled"}, 403

    access_token = create_access_token(identity=str(current_user.id))
    return {"access_token": access_token}, 200


@auth_bp.post("/logout", strict_slashes=False)
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    expires_at = datetime.fromtimestamp(token["exp"], tz=timezone.utc)

    revoked_token = TokenBlocklist(
        jti=token["jti"],
        token_type=token["type"],
        user_id=token["sub"],
        expires_at=expires_at,
    )

    db.session.add(revoked_token)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return {"message": "Token revoked"}, 200


@auth_bp.get("/me", strict_slashes=False)
@jwt_required()
def me():
    if current_user is None:
        return {"message": "User not found"}, 401

    if not current_user.is_active:
        return {"message": "User account is disabled"}, 403

    return {"user": current_user.to_dict()}, 200


def _create_token_pair(user: User) -> dict[str, str]:
    identity = str(user.id)
    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
    }


def _json_body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {}
    return data


def _validate_register_payload(data: dict) -> dict[str, str]:
    errors = {}

    email = _string_value(data, "email").strip().lower()
    username = _string_value(data, "username").strip().lower()
    password = _string_value(data, "password")
    first_name = _string_value(data, "first_name").strip()
    last_name = _string_value(data, "last_name").strip()

    if not EMAIL_PATTERN.match(email) or len(email) > 255:
        errors["email"] = "A valid email is required"

    if not 3 <= len(username) <= 100 or not USERNAME_PATTERN.match(username):
        errors["username"] = (
            "Username must be 3-100 characters and contain only lowercase letters, "
            "numbers, underscores, and hyphens"
        )

    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        errors["password"] = "Password must be 12-128 characters"

    if not 1 <= len(first_name) <= 30:
        errors["first_name"] = "First name must be 1-30 characters"

    if not 1 <= len(last_name) <= 30:
        errors["last_name"] = "Last name must be 1-30 characters"

    return errors


def _string_value(data: dict, key: str) -> str:
    value = data.get(key)
    if isinstance(value, str):
        return value
    return ""


def _login_identifier(data: dict) -> str:
    for key in ("identifier", "email", "username"):
        value = _string_value(data, key).strip().lower()
        if value:
            return value
    return ""
