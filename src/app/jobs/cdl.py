import re

import click
import httpx
from devtools import debug
from flask.cli import with_appcontext
from functional import seq
from lxml.html import fromstring

from app.extensions import db
from app.models import Solution

ROOT = "https://comptoir-du-libre.org/fr/softwares?_method=POST&reviewed=false&screenCaptured=false&hasUser=true&hasServiceProvider=true&order=softwarename.asc&search="


def register(cli):
    cli.add_command(cdl)


@click.group()
def cdl():
    """Import data from Comptoir du Libre"""


@cdl.command("import-solutions")
@with_appcontext
def import_solutions():
    r = httpx.get(ROOT)
    matches = re.findall('href="/fr/softwares/([0-9]+)"', r.text)
    cdl_ids = seq(matches).map(int).to_set()
    debug(cdl_ids)

    for cdl_id in cdl_ids:
        parse_page(cdl_id)

    db.session.commit()


def parse_page(cdl_id: int):
    r = httpx.get(f"https://comptoir-du-libre.org/fr/softwares/{cdl_id}")
    text = r.text
    document = fromstring(r.text)

    name = get_meta_property(document, "og:title")
    description = get_meta_property(document, "og:description")
    tentative_id = name.lower()

    m = re.search(
        'Site web officiel : <a href="(.*?)" rel="noopener noreferrer">', text
    )
    if m:
        home_url = m.group(1)
    else:
        home_url = ""
    print(name, home_url)

    solution = db.session.query(Solution).filter(Solution.cdl_id == cdl_id).first()
    if not solution:
        solution = (
            db.session.query(Solution).filter(Solution.id == tentative_id).first()
        )
    if not solution:
        print(f"Creating: {tentative_id}")
        solution = Solution(id=tentative_id, name=name)
        db.session.add(solution)

    solution.cdl_id = cdl_id
    solution.description = description
    solution.home_url = home_url


def get_meta_property(document, name: str) -> str:
    elem = document.cssselect(f"meta[property='{name}']")[0]
    value = elem.attrib["content"]
    return value
