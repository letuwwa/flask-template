from flask import Flask

from app.extensions import cors
from app.routers import index_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    app.register_blueprint(index_bp)

    return app
