from flask import Flask

from .routers import index_bp
from . import models as models
from .extensions import cors, db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(index_bp)

    return app
