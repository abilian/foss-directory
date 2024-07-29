from __future__ import annotations

import codecs
import csv
import json
import time
from typing import Any, cast
from zipfile import ZipFile

import click
import rich
from flask.cli import with_appcontext
from sqlalchemy.orm import Session
from tqdm import tqdm

from app.extensions import db
from app.jobs.util import count_lines, fetch_file_if_newer
from app.models import Base, SireneEtablissement, SireneUniteLegale


def register(cli):
    cli.add_command(sirene)


GOOD_NAF = {
    "26",
    "47",
    "58",
    "60",
    "62",
    "63",
    "64",
    "70",
    "71",
    "72",
    "73",
    "74",
    "82",
    "85",
}


@click.group()
def sirene():
    """Import data (unités légales & etablissements) from SIRENE"""


@sirene.command("import-all")
@with_appcontext
def import_all():
    _import_unites_legales()
    _import_etablissements()


@sirene.command("import-unites-legales")
@with_appcontext
def import_unites_legales():
    """Import des unités légales"""
    _import_unites_legales()


@sirene.command("import-etablissements")
@with_appcontext
def import_etablissements():
    """Import des établissements"""
    _import_etablissements()


def _import_unites_legales():
    delete_all(SireneUniteLegale)

    t0 = time.time()

    url = "https://files.data.gouv.fr/insee-sirene/StockUniteLegale_utf8.zip"
    zip_filename = "data/sirene/StockUniteLegale_utf8.zip"
    fetch_file_if_newer(url, zip_filename)

    zip = ZipFile(zip_filename)

    fd = zip.open("StockUniteLegale_utf8.csv")
    total = count_lines(fd)

    print(f"{total} lines to parse")

    t1 = time.time()
    print("# Elapsed time:", t1 - t0)

    fd = codecs.iterdecode(zip.open("StockUniteLegale_utf8.csv"), "utf8")
    csv_reader = csv.DictReader(fd)

    _import_csv_unites_legales(csv_reader, total)


def _import_csv_unites_legales(csv_reader, total: int):
    def make_mapping(record):
        d = {}
        for k, v in record.items():
            if k.endswith("UniteLegale"):
                kk = k[0 : -len("UniteLegale")]
            else:
                kk = k
            d[kk] = v

        siren = json_record["siren"]
        return {
            "siren": siren,
            "json": json.dumps(d),
        }

    i = 0
    mappings = []
    session: Session = cast(Session, db.session)
    for json_record in tqdm(csv_reader, total=total):
        if not check_unite_legale(json_record):
            continue

        code_ape = json_record.get("activitePrincipaleUniteLegale")
        if not code_ape:
            continue
        if code_ape[0:2] not in GOOD_NAF:
            continue

        mappings.append(make_mapping(json_record))

        i += 1
        if i % 10000 == 0:
            session.bulk_insert_mappings(SireneUniteLegale, mappings)
            db.session.commit()
            mappings = []

    session.bulk_insert_mappings(SireneUniteLegale, mappings)
    db.session.commit()


def _import_etablissements():
    delete_all(SireneEtablissement)

    url = "https://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.zip"
    zip_filename = "data/sirene/StockEtablissement_utf8.zip"
    fetch_file_if_newer(url, zip_filename)

    zip = ZipFile(zip_filename)

    rich.print("[grey54]Counting etablissements...[/grey54]")
    with zip.open("StockEtablissement_utf8.csv") as fd:
        total = count_lines(fd)

    fd = codecs.iterdecode(zip.open("StockEtablissement_utf8.csv"), "utf8")
    csv_reader = csv.DictReader(fd)

    _import_csv_etablissements(csv_reader, total)


def _import_csv_etablissements(csv_reader, total: int):
    def make_mapping(record):
        d = {}
        for k, v in record.items():
            if k.endswith("Etablissement"):
                kk = k[0 : -len("Etablissement")]
            else:
                kk = k
            d[kk] = v

        siren = json_record["siren"]
        siret = json_record["siret"]
        return {
            "siren": siren,
            "siret": siret,
            "json": json.dumps(d),
        }

    i = 0
    mappings = []
    session: Session = cast(Session, db.session)
    for json_record in tqdm(csv_reader, total=total):
        # Inactif / fermé
        if json_record.get("etatAdministratifEtablissement") != "A":
            continue

        code_ape = json_record.get("activitePrincipaleEtablissement")
        if not code_ape:
            continue
        if code_ape[0:2] not in GOOD_NAF:
            continue

        mappings.append(make_mapping(json_record))

        i += 1
        if i % 10000 == 0:
            session.bulk_insert_mappings(SireneEtablissement, mappings)
            db.session.commit()
            mappings = []

    session.bulk_insert_mappings(SireneEtablissement, mappings)
    db.session.commit()


def check_unite_legale(data: dict[str, Any]):
    etat = data.get("etatAdministratifUniteLegale")
    if etat != "A":
        return False

    # Pas les SCI
    cat_jur = data.get("categorieJuridiqueUniteLegale", "x")
    if cat_jur == "6540":
        return False

    return True


def delete_all(cls: type[Base]):
    rich.print(f"[red]Deleting table {cls.__tablename__}")
    stmt = cls.__table__.delete()
    db.session.execute(stmt)
    db.session.commit()
