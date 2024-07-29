import click
import requests
from bs4 import BeautifulSoup
from flask.cli import with_appcontext
from rich import print

from app.extensions import db
from app.models import Societe

TIMEOUT = 30


def register(cli):
    cli.add_command(metadata)


@click.group()
def metadata():
    """Crawl members websites and collect content."""


@metadata.command()
@with_appcontext
def collect():
    print("Fetching metadata from web pages (if needed)")

    societes: list[Societe] = (
        db.session.query(Societe).filter(Societe.active == True).all()
    )
    for societe in societes:
        fix_descriptions(societe)

        print()
        print(f"Fetching metadata for {societe.nom}: {societe.site_web}")

        check_metadata(societe)

        db.session.commit()


@metadata.command()
@with_appcontext
def update():
    fix_metiers()


def fix_metiers():
    for societe in db.session.query(Societe).all():
        metier = "services"

        if societe.naf_code.startswith("58.29"):
            metier = "édition"
        if societe.naf_code in {"72.19Z"}:
            metier = "édition"

        if societe.nom in ("GANDI", "OVH"):
            metier = "hébergement"

        if societe.metier != metier:
            print(f"[green]Updating {societe.nom} with metier:[/green] {metier}")
            societe.metier = metier

    db.session.commit()


def fix_descriptions(societe):
    if not societe.description_short:
        societe.description_short = societe.description
    if not societe.description_long:
        societe.description_long = societe.description


def check_metadata(societe: Societe):
    url = societe.site_web
    # debug(url)
    try:
        # result = httpx.get(url, timeout=20, follow_redirects=True, verify=False)
        headers = {"User-Agent": "Python Requests"}
        result = requests.get(url, headers=headers, timeout=20, verify=False)
        status = result.status_code
    except OSError as e:
        print(f"[red]error: {e}[/red]")
        status = -1

    if status != 200:
        print(f"[red]### {societe.nom}: {url} -> {status}[/red]")
        societe.site_web_down = True
        return

    societe.site_web_down = False

    html = result.content
    soup = BeautifulSoup(html, features="lxml")
    all_metas = soup.find_all("meta")
    for meta in all_metas:
        name = meta.attrs.get("name", "")
        property = meta.attrs.get("property", "")
        content = meta.attrs.get("content", "")

        if (name == "description" or property == "og:description") and content:
            if content == societe.description:
                continue

            update_description(societe, content)
            return


def update_description(societe: Societe, description: str):
    print(f"[green]Updating {societe.nom} with description:[/green]\n{description}")
    print(f"[green]Old description:[/green]\n{societe.description}")

    societe.description_short = description

    if not societe.description_long:
        societe.description_long = description
