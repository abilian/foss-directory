"""
Export the list of free software known to Wikidata uting this query:

```
SELECT ?item ?itemLabel
WHERE
{
    ?item wdt:P31 wd:Q341 .
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
```

On https://query.wikidata.org/

Then save the result as a JSON file to data/wikidata/

"""

import json

import click
from devtools import debug

# import wptools
# from wikidata.client import Client
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Solution


def register(cli):
    cli.add_command(wikidata)


@click.group()
def wikidata():
    "Import data from wikidata (not ready for prime time)"
    pass


@wikidata.command("import-software")
@with_appcontext
def import_software():
    """Import software from wikidata. A JSON file must be present in data/."""
    import wptools

    wkd_file = "data/wikidata/software.json"
    wkd_data = json.load(open(wkd_file))

    solutions = db.session.query(Solution).all()
    for solution in solutions:
        assert solution.name in solution.aliases

        for wkd_item in wkd_data:
            wikidata_id = wkd_item["item"].split("/")[-1]
            wikidata_name = wkd_item["itemLabel"]

            if wikidata_name.lower() in {alias.lower() for alias in solution.aliases}:
                if wikidata_id != solution.wikidata_id:
                    print(f"Update: {solution.slug} '{solution.name}' {wikidata_id}")
                    solution.wikidata_id = wikidata_id
                break

    db.session.commit()

    solutions = db.session.query(Solution).all()

    for solution in solutions:
        if not solution.wikidata_id:
            continue
        page = wptools.page(wikibase=solution.wikidata_id)
        page.get_wikidata(show=False)

        debug(page)
        debug(page.data["wikidata"])

        solution.wikidata = page.data["wikidata"]


@wikidata.command("list-missing")
@with_appcontext
def list_missing():
    solutions = (
        db.session.query(Solution)
        .filter(Solution.active == True)
        .order_by(Solution.slug)
        .all()
    )
    for solution in solutions:
        if wkd_id := solution.wikidata_id:
            print(f"OK: {solution.slug} -> {wkd_id}")
            continue

        print(f"KO: '{solution.name}' - {solution.aliases}")


@wikidata.command("import")
@with_appcontext
def import_():
    solutions = db.session.query(Solution).all()
    for solution in solutions:
        parse_solution(solution)
    db.session.commit()


@wikidata.command("dump")
@with_appcontext
def dump():
    solutions = db.session.query(Solution).all()
    for solution in solutions:
        wikidata = solution.wikidata
        if not wikidata:
            continue
        lang = wikidata.get("langage de programmation (P277)")
        licence = wikidata.get("licence (P275)")
        nature = wikidata.get("nature de l'élément (P31)")
        debug(solution.name, solution.wikidata_id, nature, licence, lang)


def parse_solution(solution: Solution):
    # if solution.wikipedia_en_url:
    #     try:
    #         parse_wikipedia(solution, "en")
    #     except:
    #         pass

    if solution.wikipedia_fr_url:
        try:
            parse_wikipedia(solution, "fr")
        except:
            pass


def parse_wikipedia(solution: Solution, lang: str):
    import wptools

    print()
    url = getattr(solution, f"wikipedia_{lang}_url")
    wp_id = url.split("/")[-1].replace("_", " ").strip()
    debug(url, lang, wp_id)

    page = wptools.page(wp_id, lang=lang)

    debug(page.get(show=False))
    debug(page.get_more(show=False))
    # debug(page.data)
    debug(page.data["extract"])
    debug(page.data["wikidata"])
    solution.wikidata_id = page.data["wikibase"]
    solution.wikidata = page.data["wikidata"]

    print()

    # site = pywikibot.Site("en", "wikipedia")
    # if not solution.wikipedia_en_url:
    #     return
    # debug(wp_id)
    # page = pywikibot.Page(site, wp_id)
    # item = pywikibot.ItemPage.fromPage(page)
    # item.get()  # you need to call it to access any data.
    # debug(item)
    # print()
    # debug(item.sitelinks)
    # for link in item.sitelinks.values():
    #     debug(link)
    # debug(item.aliases)
    # print()
    # for alias in item.aliases.values():
    #     debug(alias)
    # debug(item.claims)
    # print()
    # for claim in item.claims.values():
    #     debug(claim)
    # print(78 * "-")
