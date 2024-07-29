import sqlalchemy as sa
from flask import render_template

from app.extensions import db
from app.models import Societe

from . import blueprint


@blueprint.route("/reports/")
def reports():
    stmt = sa.select(Societe).where(Societe.active == True)
    result = db.session.execute(stmt)
    societes: list[Societe] = list(result.scalars())
    societes.sort(key=lambda societe: societe.nom.lower())

    count = len(societes)

    return render_template("reports/index.html.j2", count=count, societes=societes)
