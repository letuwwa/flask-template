from flask import Flask
from .index import index_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(index_bp)


__all__ = ("index_bp", "register_blueprints")
