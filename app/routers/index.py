from flask import Blueprint


index_bp = Blueprint("basic", __name__)


@index_bp.route("/")
def index():
    return {"status": "ok"}, 200
