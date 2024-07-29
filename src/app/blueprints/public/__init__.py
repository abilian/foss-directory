from flask import Blueprint

blueprint = Blueprint("public", __name__, url_prefix="", template_folder="templates")

route = blueprint.route
