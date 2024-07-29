import json
from pathlib import Path

import click
from flask.cli import with_appcontext
from glom import glom

from app.extensions import db
from app.models import Solution


def register(cli):
    cli.add_command(afs)


@click.group()
def afs():
    """Import data from AFS ONE"""
    pass


@afs.command()
@with_appcontext
def check():
    """Import data from AFS ONE"""
    print("# Check data from AFS ONE")

    for path in Path("data/awesome-free-software").glob("*.json"):
        print("Checking", path)
        try:
            json.load(path.open())
        except json.decoder.JSONDecodeError as e:
            print(f"Error in {path}: {e}")


@afs.command()
@with_appcontext
def load():
    """Import data from AFS ONE"""
    print("# Importing from AFS ONE")

    for path in Path("data/awesome-free-software").glob("*.json"):
        import_vendor(path)

    db.session.commit()


def import_vendor(path):
    data = json.load(path.open())
    free_software_list = glom(data, "free_software_list")
    for solution_json in free_software_list:
        import_solution(solution_json)


def import_solution(solution_json):
    title = glom(solution_json, "title")
    website = glom(solution_json, "website")
    wikipedia_url = solution_json.get("wikipedia_url", "")
    afs_id = title
    tentative_id = title.lower()

    solution = db.session.query(Solution).filter(Solution.afs_id == afs_id).first()
    if not solution:
        solution = (
            db.session.query(Solution).filter(Solution.id == tentative_id).first()
        )
    if not solution:
        print(f"Creating: {tentative_id}")
        solution = Solution(id=tentative_id)
        db.session.add(solution)

    solution.afs_id = afs_id
    solution.home_url = website
    solution.wikipedia_en_url = wikipedia_url
    db.session.commit()
