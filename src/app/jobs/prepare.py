import json
import re

import click
import httpx
import requests
from devtools import debug
from flask.cli import with_appcontext

from app.extensions import db
from app.models import (
    Etablissement,
    SireneEtablissement,
    SireneUniteLegale,
    Societe,
    Solution,
)


def register(cli):
    cli.add_command(prepare)


#
# CLI commands
#
@click.group()
def prepare():
    "Prepare data"
    pass


@prepare.command("update-all")
@with_appcontext
def update_all():
    _update_societes()
    _update_etablissements()
    _geocode()


@prepare.command("update-societes")
@with_appcontext
def update_societes():
    _update_societes()


@prepare.command("update-etablissements")
@with_appcontext
def update_etablissements():
    _update_etablissements()


@prepare.command()
@with_appcontext
def geocode():
    _geocode()


#
# Actual work
#
def _update_societes():
    query = db.session.query(Societe)
    societes: list[Societe] = query.filter(Societe.active == True).all()
    for societe in societes:
        siren = societe.siren
        nom = societe.nom

        if len(siren) > 9:
            siren = siren[0:9]
        if len(siren) < 9:
            click.secho(f"Société {nom} ({siren}) siren incorrect", fg="red")

        sirene_societe = db.session.query(SireneUniteLegale).get(siren)
        if not sirene_societe:
            click.secho(f"Société {nom} ({siren}) introuvable", fg="red")
            continue

        record = sirene_societe._json
        societe._insee = json.dumps(record)

    db.session.commit()


def _update_etablissements():
    societes: list[Societe] = (
        db.session.query(Societe).filter(Societe.active == True).all()
    )

    for societe in societes:
        siren = societe.siren
        if len(siren) > 9:
            siren = siren[0:9]
        nom = societe.nom

        sirene_etablissements: list[SireneEtablissement] = (
            db.session.query(SireneEtablissement).filter_by(siren=siren).all()
        )

        if not sirene_etablissements:
            click.secho(f"La société {nom} ({siren}) n'a pas d'établissement", fg="red")
            continue

        for sirene_etablissement in sirene_etablissements:
            record = sirene_etablissement._json
            siret = record.get("siret")
            _insee = json.dumps(record)

            etablissement = db.session.query(Etablissement).get(siret)
            if etablissement:
                etablissement._insee = _insee
            else:
                etablissement = Etablissement(siret=siret, siren=siren, _insee=_insee)
                db.session.add(etablissement)

        # if not sirene_unite_legale:
        #     print(f"{siren}: skipping {nom}")
        #     continue
        #
        # societe._insee = sirene_unite_legale.json
        # pprint({*list(sirene_unite_legale._json.keys())})
        # societe.denomination_insee = sirene_unite_legale._json["denomination"]
        # print(f"{siren}: updated ({societe.nom}) -> {societe.denomination_insee}")
        #
        # domain = tldextract.extract(societe.site_web).registered_domain
        # societe.domain = domain

    db.session.commit()


def _geocode():
    etablissements: list[Etablissement] = db.session.query(Etablissement).all()

    for etablissement in etablissements:
        siret = etablissement.siret

        societe = etablissement.societe
        if not societe:
            click.secho(f"Etablissement {siret} sans société!", fg="red")
            continue

        nom = societe.nom

        data = etablissement.sirene_data
        adresse = f"{data['numeroVoie']} {data['typeVoie']} {data['libelleVoie']}"
        commune = data.get("libelleCommune", "")
        codecommune = data.get("codeCommune", "")

        params = {
            "q": adresse,
            "citycode": codecommune,
        }
        r = requests.get("http://api-adresse.data.gouv.fr/search/", params=params)

        result = r.json()
        print(nom)
        print(adresse)
        if result.get("features"):
            first_result = result["features"][0]

            print(commune, "->", first_result["properties"]["city"])

            props = first_result["properties"]
            print(
                "->\n{name}\n{city}\n{citycode} {postcode}\n{context}\n{score}".format(
                    **props
                )
            )
            # FIXME later
            etablissement._geo_data = json.dumps(first_result)
        else:
            click.secho("Address not found", fg="red")

        print(78 * "-")

    db.session.commit()


@prepare.command("parse-wikipedia")
@with_appcontext
def parse_wikipedia():
    pat = '<span class="wd_p856"><a rel="nofollow" class="external text" href="(.*?)">'

    solutions = db.session.query(Solution).all()
    for solution in solutions:
        debug(solution, solution.home_url, solution.wikipedia_fr_url)
        if solution.home_url:
            continue
        if not solution.wikipedia_fr_url:
            continue
        r = httpx.get(solution.wikipedia_fr_url)
        text = r.text
        m = re.search(pat, text)
        debug(solution, m)
        if m:
            debug(solution.name, m.group(1))
            solution.home_url = m.group(1)

    db.session.commit()
