from flask import Blueprint

blueprint = Blueprint("admin-api", __name__, url_prefix="/api/admin")
route = blueprint.route
