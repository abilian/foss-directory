import sys

import click
import openpyxl
import rich
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Societe
from app.models.cluster import Cluster


def register(cli):
    cli.add_command(import_)


@click.command("import")
@click.option("--file", "-f")
@click.option("--cluster", "-c")
@with_appcontext
def import_(file, cluster):
    "Import membres from an Excel file"

    cluster = Cluster.query.filter_by(nom=cluster).first()
    if not cluster:
        rich.print(f"[red]No such cluster: {cluster}[/red]")
        sys.exit(1)

    print(f"Importing from {file}")
    wb_obj = openpyxl.load_workbook(file)
    sheet = wb_obj.active
    for row in sheet.iter_rows():
        nom = row[0].value
        description = row[1].value
        site_web = row[2].value
        siren = str(row[3].value)
        if len(siren) > 9:
            siren = siren[:9]
        if len(siren) < 9:
            rich.print(f"[red]{nom}: Siren is too short[red]")
            continue
        # debug(nom, description, site_web, siren)

        societe: Societe
        societe = Societe.query.filter_by(siren=siren).first()
        if societe:
            print(f"Reactivating {societe.nom}")
            societe.active = True
        else:
            societe = Societe(
                nom=nom,
                description=description,
                description_short=description,
                description_long=description,
                site_web=site_web,
                siren=siren,
            )
            print(f"adding {societe.nom}")

        db.session.add(societe)
        db.session.flush()

        if cluster not in societe.clusters:
            print("  Adding HOS")
            societe.clusters.append(cluster)

        db.session.flush()

    db.session.commit()
