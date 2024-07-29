from flask import render_template

from . import blueprint


@blueprint.route("/sandbox")
def sandbox():
    return render_template("sandbox.j2")
