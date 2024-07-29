import click
from devtools import debug
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Societe, Solution


def register(cli):
    cli.add_command(dump)


@click.group()
def dump():
    pass


@click.command("all")
@with_appcontext
def dump_all():
    """Dump data to stdout"""
    societes = db.session.query(Societe).filter(Societe.active == True).all()
    naf_codes = set()
    for societe in societes:
        naf_codes.add(societe.naf_code)
        print(f"societe: {societe.naf_code} {societe.siren} {societe.nom}")
    # debug(sorted(list(naf_codes)))


@dump.command("solution")
@click.argument("slug")
@with_appcontext
def dump_solution(slug):
    """Dump solution info"""
    solution = db.session.query(Solution).filter(Solution.slug == slug).one()
    # noinspection PyTypeChecker
    vars_ = dict(sorted(vars(solution).items()))
    debug(vars_, solution._json, solution._props)


@dump.command("societe")
@click.argument("key")
@with_appcontext
def dump_societé(key):
    """Dump solution info"""
    societe = db.session.query(Societe).filter(Societe.siren == key).first()
    if not societe:
        societe = db.session.query(Societe).filter(Societe.nom.like(f"%{key}%")).first()

    if societe:
        vars_ = dict(sorted(vars(societe).items()))
        debug(vars_, societe._json)
