from flask import Flask

# Import models so Flask-Migrate sees them in db.metadata.
from . import models as models
from .routers import register_blueprints
from .extensions import register_extensions


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    register_extensions(app)
    register_blueprints(app)

    return app
