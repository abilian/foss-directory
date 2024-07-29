from __future__ import annotations

import webargs.flaskparser
from flask import abort, jsonify, request
from pydantic import BaseModel

from app.extensions import db
from app.models import Societe, Solution

from . import route


class SocieteDTO(BaseModel):
    siren: str
    nom: str
    description: str
    site_web: str
    domain: str

    ville: str
    region: str
    clusters: list[str]
    tags: list[str]

    solution_ids: list[str]

    class Config:
        orm_mode = True


pagination_args = {
    "page": webargs.fields.Int(load_default=1),
    "pageSize": webargs.fields.Int(load_default=50),
    "results": webargs.fields.Int(),
    "sortField": webargs.fields.Str(load_default="nom"),
    "sortOrder": webargs.fields.Str(load_default="ascend"),
}


@route("/api/societes/")
@webargs.flaskparser.use_args(pagination_args, location="query")
def societes(args):
    query = db.session.query(Societe).filter(Societe.active == True)
    total = query.count()

    page_size = args["pageSize"]

    sort_field = args["sortField"]
    if sort_field not in ["nom", "siren"]:
        abort(422)
    attr = getattr(Societe, sort_field)
    if args["sortOrder"] != "ascend":
        attr = attr.desc()
    query = query.order_by(attr)

    page = args["page"]
    query = query.offset((page - 1) * page_size).limit(page_size)

    societes: list[Societe] = query.all()
    societes_dto = [SocieteDTO.from_orm(s).dict() for s in societes]
    return jsonify(societes=societes_dto, total=total)


@route("/api/societes/", methods=["POST"])
def societe_new():
    societe = Societe()
    model = request.json
    societe.siren = model["siren"].strip()
    update_societe(societe, model)
    db.session.add(societe)
    db.session.commit()
    return ""


@route("/api/societes/<siren>")
def societe(siren):
    societe = db.session.query(Societe).get(siren)
    model = SocieteDTO.from_orm(societe).dict()
    return jsonify(model=model)


@route("/api/societes/<siren>", methods=["POST"])
def societe_post(siren):
    societe = db.session.query(Societe).get(siren)
    model = request.json
    update_societe(societe, model)
    db.session.commit()
    return ""


def update_societe(societe: Societe, model):
    societe.nom = model["nom"].strip()
    societe.description = model["description"].strip()
    societe.clusters = model["clusters"]
    societe.site_web = model["site_web"]
    societe.active = True
    update_solutions(societe, model["solution_ids"])


def update_solutions(societe: Societe, solution_ids):
    solutions = []
    for solution_id in solution_ids:
        solution = db.session.query(Solution).get(solution_id)
        if not solution:
            solution = Solution(id=solution_id)
            db.session.add(solution)
        solutions.append(solution)
    societe.solutions = solutions
