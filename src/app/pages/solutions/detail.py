import json

from flask import abort, current_app, jsonify, redirect
from functional import seq
from markupsafe import Markup
from pagic import Page, expose, url_for
from yarl import URL

from app.extensions import db
from app.models import Solution
from app.pages.solutions.index import SolutionsPage

PROPS = [
    {"id": "home_url", "label": "Home URL", "use_getter": True},
    {"id": "source_url", "label": "Source URL"},
    {"id": "license", "label": "Licence"},
    {"id": "sill_url", "label": "Fiche SILL", "use_getter": True},
    {"id": "creators", "label": "Créateur(s)", "use_getter": True},
    {"id": "developers", "label": "Développeur(s)", "use_getter": True},
]


class Props:
    props = PROPS

    def __init__(self, solution: Solution):
        self.solution = solution

    def __iter__(self):
        return iter(self.get_props())

    def get_props(self):
        props = []
        for _prop in self.props:
            prop = _prop.copy()
            prop_id = prop["id"]
            if prop.get("use_getter"):
                getter = getattr(self, prop_id)
                value = getter()
            else:
                value = self.solution.prop_get(prop_id)

            if isinstance(value, str) and value.startswith("http"):
                value = Markup(f'<a href="{value}">{value}</a>')

            prop["value"] = value
            if value is not None:
                props.append(prop)

        return props

    def sill_url(self) -> str | None:
        if self.solution.sill_id:
            url = URL("https://sill.etalab.gouv.fr/software")
            return str(url.with_query(name=self.solution.sill_name))
        else:
            return None

    def home_url(self) -> str | None:
        solution = self.solution

        if solution.home_url:
            return solution.home_url
        elif home_url := solution.prop_get("home_url"):
            return home_url
        elif solution.wikidata_id:
            return f"https://www.wikidata.org/wiki/{solution.wikidata_id}"
        else:
            return None

    def developers(self) -> str | None:
        solution = self.solution

        sill = solution._json.get("sill")
        if not sill:
            return None

        wkd_data = sill.get("wikidataData")
        if not wkd_data:
            return None

        developers = [c["name"] for c in wkd_data.get("developers", [])]
        return ", ".join(developers)

    def creators(self) -> str | None:
        return None


class SolutionPage(Page):
    name = "solution"
    path = "/solutions/<id>"
    parent = SolutionsPage

    solution: Solution | None = None

    def hydrate(self):
        id = self.args["id"]
        query = db.session.query(Solution)
        solution: Solution = query.get(id) or query.filter(Solution.name == id).first()
        if not solution:
            abort(404)
        self.solution = solution

    def context(self):
        self.hydrate()

        prestataires = sorted(self.solution.societes.copy(), key=lambda s: s.nom)
        prestataires = seq(prestataires).filter(lambda p: p.active)

        return {
            "solution": self.solution,
            "props": Props(self.solution).get_props(),
            "prestataires": prestataires,
        }

    @expose
    def screenshot(self):
        self.hydrate()

        solution = self.solution
        config = current_app.config
        if solution.screenshot_id:
            url = f"{config['S3_PUBLIC_URL']}/{solution.screenshot_id}"
            return redirect(url)
        else:
            return redirect(url_for("static", filename="img/question-mark.png"))

    @expose
    def json(self):
        self.hydrate()
        solution = self.solution
        # noinspection PyTypeChecker
        vars_ = dict(sorted(vars(solution).items()))
        kill = []
        for var in vars_:
            try:
                json.dumps(vars_[var])
            except TypeError:
                kill.append(var)
        for var in kill:
            del vars_[var]
        return jsonify(vars=vars_, json=solution._json, props=solution._props)


@url_for.register
def url_for_solution(solution: Solution):
    return url_for("solution", id=solution.id)
