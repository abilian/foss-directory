from collections import Counter

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.jobs.nlp_spacy import analyze_with_spacy
from app.jobs.nlp_textrazor import analyse_with_tz
from app.models import Societe


def register(cli):
    cli.add_command(nlp)


@click.group()
def nlp():
    "NLP jobs (Spacy, TextRazor)"
    pass


@nlp.command("with-textrazor")
@click.option("--overwrite", "-o", is_flag=True)
@with_appcontext
def with_textrazor(overwrite=False):
    for societe in _get_societes():
        if societe.topics and not overwrite:
            # print("Skipping")
            # debug(societe.topics)
            continue

        title = f"Analyzing company {societe.nom}"
        print(title)
        print("=" * len(title))
        print()

        analyse_with_tz(societe)
        db.session.commit()

        print()


@nlp.command("with-spacy")
@click.option("--overwrite", "-o", is_flag=True)
@with_appcontext
def with_spacy(overwrite=False):
    all_entities = Counter()
    for societe in _get_societes():
        if societe.topics and not overwrite:
            continue

        # print(title)
        # print("=" * len(title))
        # print()

        entities = analyze_with_spacy(societe)
        # db.session.commit()
        # debug(entities)

        # print()
        all_entities.update(entities)

    for entity, n in all_entities.most_common():
        print(n, entity)
    print()


def _get_societes():
    societes = (
        db.session.query(Societe)
        .filter(Societe.active == True)
        .order_by(Societe.nom)
        .all()
    )
    return societes
