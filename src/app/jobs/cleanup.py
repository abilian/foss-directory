import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Page, Societe, Solution


def register(cli):
    cli.add_command(cleanup)


@click.command("cleanup")
@with_appcontext
def cleanup():
    "Clean up (remove) inactive societes and solutions"
    cleanup_societes()
    cleanup_solutions()
    fix()
    db.session.commit()


def cleanup_societes():
    societes: list[Societe] = db.session.query(Societe).all()
    for societe in societes:
        if not societe.clusters and societe.active:
            societe.active = False
            click.echo(f"Cleaning up {societe.nom}")


def cleanup_solutions():
    solutions: list[Solution] = db.session.query(Solution).all()
    for solution in solutions:
        societes = solution.societes
        solution.active = any(societe.active for societe in societes)


def fix():
    pages = db.session.query(Page).filter(Page.text != "").all()
    for page in pages:
        if len(page.text) > 100000:
            page.text = page.text[0:10000]
