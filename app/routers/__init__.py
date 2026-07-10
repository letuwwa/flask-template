from flask import Flask

from .auth import auth_bp
from .index import index_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)


__all__ = ("index_bp", "auth_bp", "register_blueprints")
