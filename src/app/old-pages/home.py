import webargs
from flask import render_template, request
from pagic import Page, url_for
from sqlalchemy import func, text
from webargs.flaskparser import parser

from app.extensions import db
from app.models import Societe
from app.pages.societe import SocietePage

filter_args_specs = {
    "page": webargs.fields.Int(load_default=1),
    "q": webargs.fields.Str(load_default=""),
    "metier": webargs.fields.Str(load_default=""),
    "region": webargs.fields.Str(load_default=""),
}


class HomePage(Page):
    name = "home"
    path = ""
    menu = "main"
    children = [SocietePage]

    def get(self):
        if request.headers.get("Hx-Request"):
            ctx = self.context()
            return render_template("pages/home--list.j2", **ctx)
        return super().get()

    def context(self):
        args = parser.parse(filter_args_specs, request, location="query")

        query = (
            db.session.query(Societe)
            .filter(Societe.active == True)
            .order_by(func.lower(Societe.nom))
        )

        q = args["q"].lower()
        if q:
            query = query.filter(func.lower(Societe.nom).like(f"%{q}%"))

        metier = args["metier"]
        if metier:
            query = query.filter(Societe.metier == metier)

        region = args["region"]
        if region:
            clause = text("_regions @> to_jsonb((:region)::text)").bindparams(
                region=region
            )
            query = query.filter(clause)

        total = query.count()

        page = args["page"]
        if page <= 1:
            page = 1
        query = query.offset((page - 1) * 24).limit(24)

        societes: list[Societe] = query.all()

        # Quick hack
        all = (
            db.session.query(Societe)
            .filter(Societe.active == True)
            .order_by(Societe.nom)
        ).all()
        regions = {s.region for s in all}
        regions = [{"label": r, "selected": r == region} for r in sorted(regions)]
        metiers = {s.metier for s in all}
        metiers = [{"label": m, "selected": m == metier} for m in sorted(metiers)]

        next_page_args = args.copy()
        next_page_args["page"] = page + 1
        next_page = url_for(".home", **next_page_args)

        if page > 1:
            prev_page_args = args.copy()
            prev_page_args["page"] = page - 1
            prev_page = url_for(".home", **prev_page_args)
        else:
            prev_page = ""

        return {
            "args": args,
            "societes": societes,
            "regions": regions,
            "metiers": metiers,
            "total": total,
            "title": "Annuaire du CNLL",
            "subtitle": "Les entreprises du logiciel libre en France",
            "page": page,
            "next_page": next_page,
            "prev_page": prev_page,
        }
