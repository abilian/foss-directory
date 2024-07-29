from pagic import Page
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Solution


class SolutionsPage(Page):
    menu = "main"
    menu_order = 100

    name = "solutions"
    path = "/solutions/"

    label = "Solutions & Technologies"
    title = (
        "Les principales technologies et solutions supportées par les membres du CNLL"
    )

    def context(self):
        solutions = (
            db.session.query(Solution)
            .filter(Solution.active)
            .options(joinedload(Solution.societes))
            .order_by(Solution.slug)
            .all()
        )

        return {"solutions": solutions}
