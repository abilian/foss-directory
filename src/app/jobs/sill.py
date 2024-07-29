from __future__ import annotations

import json

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.jobs.util import fetch_file_if_newer
from app.models import Solution


def register(cli):
    cli.add_command(sill)


@click.group()
def sill():
    """Import data from SILL"""


@sill.command("import")
@with_appcontext
def import_():
    url = "https://sill.etalab.gouv.fr/api/sill.json"
    filename = "data/sill.json"
    fetch_file_if_newer(url, filename)
    sill = json.load(open(filename))

    solutions = db.session.query(Solution).order_by(Solution.slug).all()

    for record in sorted(sill["catalog"], key=lambda x: x["name"].lower()):
        try_merge(record, solutions)

    db.session.commit()


def try_merge(record, solutions):
    name = record["name"]
    for solution in solutions:
        aliases = solution._json.get("aliases", [])
        for alias in aliases:
            if alias.lower() == name.lower():
                print(f"Found {name} -> {solution.id}")
                do_merge(record, solution)
                return

    print(f"Not found {name}")


def do_merge(record, solution):
    solution.sill_id = record["id"]
    solution._json["sill"] = record

    if function := record.get("function"):
        solution.prop_set("tagline", function)
        if not solution.description:
            solution.description = function

    if license := record.get("license"):
        solution.prop_set("license", license)

    if wikidata := record.get("wikidataData"):
        solution.wikidata_id = wikidata["id"]

        if home_url := wikidata.get("websiteUrl"):
            solution.prop_set("home_url", home_url)
            if not solution.home_url:
                solution.home_url = home_url

        if source_url := wikidata.get("sourceUrl"):
            solution.prop_set("source_url", source_url)
