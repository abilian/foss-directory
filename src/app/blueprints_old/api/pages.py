from collections import Counter
from pathlib import Path

from flask import jsonify, render_template
from mistune import markdown

from app.extensions import db
from app.models import Societe

from . import route


@route("/pages/faq/")
def faq():
    body_src = Path("content/faq.md").open().read()
    body = markdown(body_src)
    ctx = {
        "title": "A propos / FAQ",
        "body": body,
    }
    return jsonify(ctx)


@route("/pages/clusters/")
def clusters():
    count = make_count("clusters")
    ctx = {
        "title": "Clusters membres du CNLL",
        "body": render_template("clusters.j2", clusters=count),
    }
    return jsonify(ctx)


@route("/pages/regions/")
def regions():
    count = make_count("regions")
    ctx = {
        "title": "Régions",
        "body": render_template("regions.j2", regions=count),
    }
    return jsonify(ctx)


@route("/pages/villes/")
def villes():
    count = make_count("villes")
    ctx = {
        "title": "Villes",
        "body": render_template("villes.j2", villes=count),
    }
    return jsonify(ctx)


def get_societes() -> list[Societe]:
    societes: list[Societe] = (
        db.session.query(Societe)
        .filter(Societe.active == True)
        .order_by(Societe.nom)
        .all()
    )
    return societes


def make_count(attr):
    societes = get_societes()
    counter = Counter()
    for s in societes:
        counter.update(getattr(s, attr))

    count = list(counter.items())

    def sorter(t):
        return (-t[1], t[0])

    count.sort(key=sorter)
    return count
