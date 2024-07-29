from pprint import pprint
from typing import Any

import click
import ramda as r
from airtable import Airtable
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Societe

BASE_ID = "appHGARFMQ41wig9a"
API_KEY = "keyEXgejL6gKr3ywt"
table = Airtable(BASE_ID, "Sociétés", api_key=API_KEY)


def register(cli):
    pass
    # cli.add_command(airtable_sync)


@click.command("airtable-sync")
@with_appcontext
def airtable_sync():
    """Sync with Airtable (obsolete)"""
    session = db.session

    records = table.get_all(maxRecords=1000)

    for i, record in enumerate(records):
        pprint(record)
        fields = record["fields"]
        siren = fields.get("SIREN")
        if not siren:
            continue

        societe = session.query(Societe).get(siren)
        if not societe:
            societe = Societe(siren=siren)
            session.add(societe)

        update_from_record(societe, fields)

        fix_siren(record)
        fix_web(record)
        fix_denomination(record, societe)

        # sync_tags(record, societe)

        print(societe._extra)
        session.commit()


def update_from_record(societe: Societe, fields: dict[str, Any]):
    societe.nom = fields.get("NOM", "")
    societe.active = fields.get("Active", False)
    societe.site_web = fields.get("SITE WEB", "")
    societe.clusters = fields.get("Cluster", [])
    societe.description = fields.get("DESCRIPTION")


def fix_siren(record: dict[str, Any]):
    id = record["id"]
    fields = record["fields"]

    siren = fields.get("SIREN")
    if siren and len(siren) == 14:
        old_siren = siren
        siren = siren[0:9]
        print(f"Updating siren for {fields['NOM']}: {old_siren} -> {siren}")
        table.update(id, {"SIREN": siren})
        # pprint(status)


def fix_web(record):
    id = record["id"]
    fields = record["fields"]

    url = fields.get("SITE WEB")
    if not url:
        return

    if not url.startswith("http"):
        old_url = url
        url = "http://" + url
        print(f"Updating url for {fields['NOM']}: {old_url} -> {url}")
        table.update(id, {"SITE WEB": url})


def fix_denomination(record: dict[str, Any], societe: Societe):
    id = record["id"]
    fields = record["fields"]

    denomination = fields.get("Denomination INSEE")
    if denomination != societe.denomination_insee:
        print(f"Updating denomination for {fields['NOM']}")
        table.update(id, {"Denomination INSEE": societe.denomination_insee})


def sync_tags(record, societe: Societe):
    id = record["id"]
    fields = record["fields"]
    siren = fields.get("SIREN")
    if not siren:
        return

    topics = "\n".join(r.map(lambda topic: topic["label"], societe.topics))
    table.update(id, {"Topics": topics})

    entities = "\n".join(r.map(lambda entity: entity["id"], societe.entities))
    table.update(id, {"Entities": entities})

    solutions = "\n".join(r.map(lambda solution: solution.id, societe.solutions))
    table.update(id, {"Solutions": solutions})
