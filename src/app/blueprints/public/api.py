import sqlalchemy as sa
from flask import jsonify
from functional import seq

from app.extensions import db
from app.models import Solution

from . import blueprint


@blueprint.route("/api/prestataires-sill.json")
def prestataires_sill_json():
    stmt = (
        sa.select(Solution)
        .where(Solution.active == True)
        .where(Solution.sill_id != None)
    )
    result = db.session.execute(stmt)
    solutions: list[Solution] = list(result.scalars())

    output = []
    for solution in solutions:
        societes = seq(solution.societes).filter(lambda societe: societe.active == True)
        if societes:
            output.append(
                {
                    "nom": solution.name,
                    "sill_id": solution.sill_id,
                    "prestataires": [
                        {
                            "nom": societe.nom,
                            "siren": societe.siren,
                            "url": f"https://annuaire.cnll.fr/societes/{societe.siren}",
                        }
                        for societe in societes
                    ],
                }
            )

    return jsonify(output)
