from __future__ import annotations

import sys

import webargs.flaskparser
from flask import abort, jsonify, request
from pydantic import BaseModel

from app.extensions import db
from app.models import Solution

from . import route


class SolutionDTO(BaseModel):
    id: str
    name: str | None
    description: str

    class Config:
        orm_mode = True


pagination_args = {
    "page": webargs.fields.Int(load_default=1),
    "pageSize": webargs.fields.Int(load_default=sys.maxsize),
    "results": webargs.fields.Int(),
    "sortField": webargs.fields.Str(load_default="id"),
    "sortOrder": webargs.fields.Str(load_default="ascend"),
}


@route("/api/solutions/")
@webargs.flaskparser.use_args(pagination_args, location="query")
def solutions(args):
    query = db.session.query(Solution)
    total = query.count()

    page_size = args["pageSize"]

    sort_field = args["sortField"]
    if sort_field not in ["id"]:
        abort(422)
    attr = getattr(Solution, sort_field)
    if args["sortOrder"] != "ascend":
        attr = attr.desc()
    query = query.order_by(attr)

    page = args["page"]
    query = query.offset((page - 1) * page_size).limit(page_size)

    solutions: list[Solution] = query.all()

    solutions_dto = [SolutionDTO.from_orm(s).dict() for s in solutions]
    return jsonify(solutions=solutions_dto, total=total)


@route("/api/solutions/<id>")
def solution(id):
    solution = db.session.query(Solution).get(id)
    return jsonify(model=SolutionDTO.from_orm(solution).dict())


@route("/api/solutions/", methods=["POST"])
def solution_new():
    model = request.json
    solution = Solution()
    solution.id = model["id"].strip()
    solution.description = model["description"].strip()
    db.session.add(solution)
    db.session.commit()
    return ""


@route("/api/solutions/<id>", methods=["POST"])
def solution_post(id):
    solution = db.session.query(Solution).get(id)
    model = request.json
    solution.description = model["description"].strip()
    db.session.commit()
    return ""


@route("/api/solutions/<id>", methods=["DELETE"])
def solution_delete(id):
    solution = db.session.query(Solution).get(id)
    db.session.delete(solution)
    db.session.commit()
    return ""
