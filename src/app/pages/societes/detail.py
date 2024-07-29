from flask import current_app, redirect
from pagic import Page, expose, url_for

from app.extensions import db
from app.models import Societe
from app.pages.index import HomePage


class SocietePage(Page):
    name = "societe"
    model_name = "societe"
    path = "/societes/<siren>"
    parent = HomePage

    societe: Societe | None = None

    def hydrate(self):
        siren = self.args["siren"]
        societe: Societe = db.session.query(Societe).get(siren)
        self.societe = societe

    def context(self):
        self.hydrate()
        solutions = self.societe.solutions

        # Temp hack: dedupe
        d = {s.name: s for s in solutions}
        solutions = sorted(d.values(), key=lambda s: s.name)

        etablissements = self.societe.etablissements

        return {
            "title": f"Société: {self.societe.nom}",
            "societe": self.societe,
            "solutions": solutions,
            "etablissements": etablissements,
        }

    @expose
    def screenshot(self):
        self.hydrate()
        config = current_app.config
        if self.societe.screenshot_id:
            url = f"{config['S3_PUBLIC_URL']}/{self.societe.screenshot_id}"
            return redirect(url)
        else:
            return redirect(url_for("static", filename="img/question-mark.png"))


@url_for.register
def url_for_societe(societe: Societe, _ns="", **kw):
    return url_for("societe", siren=societe.siren)
