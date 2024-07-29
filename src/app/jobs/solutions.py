import re
from typing import Any

import click
import requests
from bs4 import BeautifulSoup
from click import secho
from devtools import debug
from flask.cli import with_appcontext
from lxml.html.clean import Cleaner

from app.extensions import db
from app.models import Societe, Solution

BLACKLIST = {
    "MacOS",
    "IOS",
    "Instagram",
    "Hyper-V",
    "Active Directory",
    "Active Server Pages",
    "AdWords",
    "IOS",
    "App Store",
    "Internet Explorer",
    "Safari (navigateur web)",
    "Skype",
    "WebSphere",
    "WhatsApp",
    "Dropbox",
    "Delphi",
    "World of Warcraft",
    "G Suite",
    "ICloud",
    "Matlab",
    "MATLAB",
    "Jira",
    "Rançongiciel",
    "Presse-papier (informatique)",
    "Opera",
    "SAP (progiciel)",
    "AIX",
    "AdSense",
    "WHOIS",
    "Whois",
    "VxWorks",
    "Visual Basic",
    "TeamViewer",
    "Spotify",
    "Simulink",
    "SharePoint",
    "Safari (web browser)",
    "QNX",
    "Opera (web browser)",
    "Office 365",
    "Minecraft",
    "HyperCard",
    "HP-UX",
    "Facebook Messenger",
    "Dropbox (service)",
    "Documentum",
    "Delphi (langage)",
    "Battlefield (série de jeux vidéo)",
    "Amazon Web Services",
    "Amazon Elastic Compute Cloud",
    "TikTok",
    "IRIX",
    "Debugger",
    "Bitcoin",
    "Paquet (logiciel)",
    "Discord (logiciel)",
}

BRANDS = {
    "Windows",
    "Microsoft",
    "Google",
    "IBM",
    "Oracle",
    "Adobe",
    "VMware",
    "Slack",
}


def register(cli):
    cli.add_command(solutions)


@click.group()
def solutions():
    """Manage solutions"""


# @solutions.command()
# @with_appcontext
# def rebuild():
#     """Rebuild solution table from NLP info"""
#     # reset()
#     update_relations()
#     update_solutions()
#     db.session.commit()


@solutions.command()
@click.argument("src_id")
@click.argument("dst_id")
@with_appcontext
def merge(src_id, dst_id):
    """Merge solutions src_id into dst_id"""
    debug(src_id, dst_id)

    src = db.session.query(Solution).filter(Solution.slug == src_id).one()
    dst = db.session.query(Solution).filter(Solution.slug == dst_id).one()

    merge_solutions(dst, src)
    db.session.commit()


@solutions.command()
@click.argument("slug")
@with_appcontext
def dump(slug):
    """Dump solution info"""
    solution = db.session.query(Solution).filter(Solution.slug == slug).one()
    # noinspection PyTypeChecker
    vars_ = dict(sorted(vars(solution).items()))
    debug(vars_, solution._json, solution._props)


@solutions.command()
@click.argument("slugs", nargs=-1)
@with_appcontext
def rm(slugs):
    """Remove solutions"""
    for slug in slugs:
        debug(slug)
        solution = db.session.query(Solution).filter(Solution.slug == slug).one()

        db.session.delete(solution)

    db.session.commit()


@solutions.command()
@with_appcontext
def fix():
    for solution in db.session.query(Solution).all():
        if solution.home_url == "http://":
            solution.home_url = ""
    db.session.commit()


def merge_solutions(dst: Solution, src: Solution):
    """Merge src into dst."""
    print(f"Merging {src.id} into {dst.id}")

    dst.name = dst.name or src.name

    dst.home_url = dst.home_url or src.home_url
    dst.wikipedia_en_url = dst.wikipedia_en_url or src.wikipedia_en_url
    dst.wikipedia_fr_url = dst.wikipedia_fr_url or src.wikipedia_fr_url

    dst.screenshot_id = dst.screenshot_id or src.screenshot_id
    dst.logo_id = dst.logo_id or src.logo_id
    dst.sill_id = dst.sill_id or src.sill_id
    dst.cdl_id = dst.cdl_id or src.cdl_id
    dst.afs_id = dst.afs_id or src.afs_id

    dst.wikidata_id = dst.wikidata_id or src.wikidata_id
    dst.wikidata = dst.wikidata or src.wikidata

    dst.description = dst.description or src.description

    dst.societes.extend(src.societes)

    for alias in src.aliases:
        dst.add_alias(alias)

    db.session.delete(src)
    db.session.commit()


def reset():
    for societe in get_societes():
        societe.solutions = []
    db.session.commit()

    db.session.query(Solution).delete()
    db.session.commit()


def update_relations():
    for societe in get_societes():
        print(f"# Société: {societe.nom}")
        update_societe(societe)
        print()


def get_societes():
    return db.session.query(Societe).order_by(Societe.nom).all()


def update_societe(societe: Societe):
    entities: list[dict[str, Any]] = societe.entities  # type: ignore
    for entity in entities:
        if "Software" in entity["dbpedia_types"]:
            entity_id = entity["id"]
            if is_blacklisted(entity_id):
                # print(f"Blacklisted: {entity_id}")
                continue

            solution = db.session.query(Solution).get(entity_id)
            if not solution:
                solution = Solution(id=entity_id)
                db.session.add(solution)

            if solution not in societe.solutions:
                print(f"Adding: {entity_id}")
                societe.solutions.append(solution)

        db.session.commit()


def is_blacklisted(solution):
    for brand in BRANDS:
        if re.search(brand, solution):
            return True
    return solution in BLACKLIST


def update_solutions():
    for solution in db.session.query(Solution).all():
        if not solution.name:
            solution.name = solution.id

        result = requests.get("https://fr.wikipedia.org/wiki/" + solution.id)
        debug(solution.id, result)
        if result.status_code != 200:
            continue

        if not result.content:
            continue

        soup = BeautifulSoup(result.content, features="lxml")
        elt = soup.find(class_="mw-parser-output")
        description = ""
        for child in elt.children:
            if child.name == "p":
                description += str(child) + "\n"
            if child.name == "h2":
                break

        description = description.strip()
        if not description:
            secho(f"Skipping {solution.id}", fg="red")
            continue

        cleaner = Cleaner(remove_tags=("a",), kill_tags=("sup",))
        description = cleaner.clean_html(description)
        solution.description = description.strip()

        # print(solution.id)
        # print(solution.description)
        # print()
        # sys.exit()

    db.session.commit()
