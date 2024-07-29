from flask import abort, current_app, redirect
from flask_admin import expose
from pagic import Page, url_for
from pydantic import BaseModel
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Societe, Solution


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


class SolutionPage(Page):
    name = "solution"
    path = "<id>"

    def context(self):
        id = self.args["id"]
        query = db.session.query(Solution)
        solution: Solution = query.get(id) or query.filter(Solution.name == id).first()
        if not solution:
            abort(404)
        return {
            "solution": SolutionDTO.from_orm(solution).dict(),
        }

    @expose
    def screenshot(self, id):
        solution: Solution = db.session.query(Solution).get(id)
        config = current_app.config
        if solution.screenshot_id:
            url = f"{config['S3_PUBLIC_URL']}/{solution.screenshot_id}"
            return redirect(url)
        else:
            return redirect(url_for("static", filename="img/question-mark.png"))


class SolutionsPage(Page):
    name = "solutions"
    label = "Solutions"
    title = (
        "Les principales technologies et solutions supportées par les membres du CNLL"
    )
    # menu = "main"
    children = [SolutionPage]

    def context(self):
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

        return {"solutions": solutions_dto}


@url_for.register
def url_for_solution(solution: Solution):
    return url_for("solution", id=solution.id)
