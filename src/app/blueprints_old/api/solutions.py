from flask import abort, current_app, jsonify, redirect, url_for
from pydantic import BaseModel
from sqlalchemy.orm import joinedload

from app.extensions import cache, db
from app.models import Societe, Solution

from . import route


class SocieteDTO(BaseModel):
    siren: str
    nom: str

    class Config:
        orm_mode = True


class SolutionDTO(BaseModel):
    id: str
    name: str
    description: str
    description_as_text: str
    tagline: str

    home_url: str
    wikipedia_fr_url: str
    wikipedia_en_url: str
    wikidata_id: str

    screenshot_id: str
    logo_id = str

    # Backref
    societes: list[SocieteDTO]

    class Config:
        orm_mode = True


@route("/solutions/")
@cache.cached(timeout=60)
def solutions():
    solutions = (
        db.session.query(Solution)
        .filter(Solution.active == True)
        .options(joinedload(Solution.societes))
        .order_by(Solution.id)
        .all()
    )
    solutions_dto = map(
        lambda solution: SolutionDTO.from_orm(solution).dict(), solutions
    )
    # Hack!
    solutions_dto = list(solutions_dto)
    for solution in solutions_dto:
        x = []
        for societe_dto in solution["societes"]:
            societe = db.session.query(Societe).get(societe_dto["siren"])
            if not societe.clusters:
                continue
            x.append(societe_dto)
        solution["societes"] = x
    # /Hack
    return jsonify(solutions=list(solutions_dto))


@route("/solutions/<id>/")
def solution(id):
    query = db.session.query(Solution)
    solution: Solution = query.get(id) or query.filter(Solution.name == id).first()
    if not solution:
        abort(404)
    return jsonify(solution=SolutionDTO.from_orm(solution).dict())


# @route("/doc/")
# @route("/doc/<path:path>")
# def doc(path=""):
#     file_path = "content/" + path
#     if os.path.isdir(file_path):
#         file_path += "/index.rst"
#     if not os.path.isfile(file_path):
#         abort(404)
#     with open(file_path) as f:
#         raw = f.read()
#
#     parts = publish_parts(source=raw, writer_name="html4css1")
#     # settings_overrides=settings)
#
#     # pprint(rendered)
#     body = Markup(parts["fragment"])
#     title = Markup(parts["title"]).striptags()
#     return render_template("page.j2", body=body, title=title)


@route("/solutions/<id>/screenshot")
def screenshot_solution(id):
    solution: Solution = db.session.query(Solution).get(id)
    config = current_app.config
    if solution.screenshot_id:
        url = f"{config['S3_PUBLIC_URL']}/{solution.screenshot_id}"
        return redirect(url)
    else:
        return redirect(url_for("static", filename="img/question-mark.png"))
