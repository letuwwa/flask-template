from flask import Flask
from app.routers import index_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(index_bp)
    return app
