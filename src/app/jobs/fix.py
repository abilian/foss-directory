import click
import httpx
from flask.cli import with_appcontext
from slugify import slugify

from app.extensions import db
from app.models import Societe, Solution


def register(cli):
    cli.add_command(fix)


@click.group()
@with_appcontext
def fix():
    "Random fixes."
    # fix1()
    # fix2()
    # fix3()
    # fix_urls()

    # fix_solutions_2()

    db.session.commit()


@fix.command("fix-solutions-1")
@with_appcontext
def fix_solutions_1():
    i = 0
    solutions = db.session.query(Solution).all()
    for solution in solutions:
        i += 1
        solution.new_id = i
        aliases = {solution.id}
        if solution.name:
            aliases.add(solution.name.lower())
        solution._json["aliases"] = list(aliases)

    db.session.commit()

    for societe in db.session.query(Societe).all():
        solution_ids = [solution.new_id for solution in societe.solutions]
        societe._json["solution_ids"] = solution_ids

    db.session.commit()


@fix.command("fix-solutions-2")
@with_appcontext
def fix_solutions_2():
    id_to_solution = {
        solution.id: solution for solution in db.session.query(Solution).all()
    }

    for societe in db.session.query(Societe).all():
        solutions = [
            id_to_solution[solution_id] for solution_id in societe._json["solution_ids"]
        ]
        societe.solutions = solutions

    for solution in db.session.query(Solution).all():
        if solution.slug:
            continue
        solution.slug = slugify(solution.name or solution.old_id)

    db.session.commit()


@fix.command("fix-solutions-3")
@with_appcontext
def fix_solutions_3():
    for solution in db.session.query(Solution).all():
        if not solution.name:
            solution.name = solution.old_id

        if "(" in solution.name:
            solution.name = solution.name.split("(")[0].strip()
            db.session.commit()

        solution.slug = slugify(solution.name)

        solution.add_alias(solution.name)
        solution.add_alias(solution.slug)

        solution.old_id = solution.old_id.lower()

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

    db.session.delete(src)
    db.session.commit()


@fix.command("fix-solutions-4")
@with_appcontext
def fix_solutions_4():
    solutions = db.session.query(Solution).order_by(Solution.slug).all()

    prev = solutions[0]
    for solution in solutions[1:]:
        if solution.slug == prev.slug:
            merge_solutions(solution, prev)

        prev = solution

    db.session.commit()

    solutions = db.session.query(Solution).order_by(Solution.slug).all()
    for solution in solutions:
        solution.active = len(solution.societes) > 0

    db.session.commit()


def fix_urls():
    societes = db.session.query(Societe).all()
    for societe in societes:
        fix_url(societe, "site_web")

    solutions = db.session.query(Solution).all()
    for solution in solutions:
        fix_url(solution, "home_url")


def fix_url(obj, name: str):
    old_url = url = getattr(obj, name)

    if url == "http://":
        url = ""
    if url.strip() == url:
        url = url.strip()
    if url != old_url:
        print(f"Fixing URL: {old_url} -> {url}")
        setattr(obj, name, url)


def fix3():
    solutions = db.session.query(Solution).all()
    for solution in solutions:
        if not solution.name:
            solution.name = solution.id

        solution.home_url = solution.home_url or ""
        solution.wikipedia_en_url = solution.wikipedia_en_url or ""
        solution.wikipedia_fr_url = solution.wikipedia_fr_url or ""
        solution.screenshot_id = solution.screenshot_id or ""
        solution.logo_id = solution.logo_id or ""


def fix2():
    solutions = db.session.query(Solution).all()
    for solution in solutions:
        old_id = solution.id
        solution.id = old_id.lower()
        try:
            db.session.commit()
        except:
            print(f"Can't commit change to {old_id}")
            db.session.rollback()
            continue


def fix1():
    solutions = db.session.query(Solution).all()
    for solution in solutions:
        old_id = solution.id

        if solution.name:
            continue

        solution.name = old_id.split("(")[0].strip()
        solution.id = solution.name.lower()

        try:
            db.session.commit()
        except:
            print(f"Can't commit change to {old_id}")
            db.session.rollback()
            continue

        url = f"https://fr.wikipedia.org/wiki/{old_id.replace(' ', '_')}"
        r = httpx.get(url)
        if r.status_code == 200:
            solution.wikipedia_fr_url = url
            continue

        url = f"https://en.wikipedia.org/wiki/{old_id.replace(' ', '_')}"
        r = httpx.get(url)
        if r.status_code == 200:
            solution.wikipedia_en_url = url
            continue

        db.session.commit()
