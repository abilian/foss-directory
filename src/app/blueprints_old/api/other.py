from flask import jsonify

from app.extensions import db
from app.models import Societe, Solution

from . import route


@route("/routes/")
def routes():
    societes = db.session.query(Societe).all()
    routes1 = [f"/societes/{societe.siren}/" for societe in societes]

    solutions = db.session.query(Solution).all()
    routes2 = [f"/solutions/{solution.id}/" for solution in solutions]

    return jsonify(routes1 + routes2)
