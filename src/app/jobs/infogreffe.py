import json

import click
import ijson
import rich
import toolz
from devtools import debug
from flask.cli import with_appcontext

from app.extensions import db
from app.jobs.util import fetch_file_if_newer
from app.models import Societe


def register(cli):
    cli.add_command(infogreffe)


@click.group()
def infogreffe():
    """Import data from Infogreffe"""


@infogreffe.command("import-infos-cles")
@click.argument("year", type=int)
@with_appcontext
def import_infos_cles(year):
    filename = f"data/infogreffe/chiffres-cles-{year}.json"
    url = f"https://opendata.datainfogreffe.fr/explore/dataset/chiffres-cles-{year}/download/?format=json"
    fetch_file_if_newer(url, filename)

    societes = db.session.query(Societe).filter(Societe.active == True).all()
    sirens = {s.siren for s in societes}

    with open(filename, "rb") as jsonfile:
        records = ijson.items(jsonfile, "item.fields")
        for record in records:
            siren = record.get("siren")
            if not siren:
                continue
            if siren not in sirens:
                continue

            record = dict(sorted(record.items()))
            rich.print(f"[green]{record['denomination']}[/green]")
            debug(record)
            print()

            # pprint(obj)
            # self.import_object(record)


@infogreffe.command("import-societes-radiees")
@click.argument("year", type=int)
@with_appcontext
def import_societes_radiees(year):
    filename = f"data/infogreffe/societes-radiees-{year}.json"

    if year == 2022:
        url = f"https://opendata.datainfogreffe.fr/explore/dataset/entreprises-radiees-en-{year}/download/?format=json"
    elif year >= 2023:
        url = f"https://opendata.datainfogreffe.fr/api/explore/v2.1/catalog/datasets/entreprises-radiees-en-{year}/exports/json"
    else:
        url = f"https://opendata.datainfogreffe.fr/explore/dataset/societes-radiees-{year}/download/?format=json"

    fetch_file_if_newer(url, filename)

    maj_radiations(filename)


def maj_radiations(filename):
    societes = db.session.query(Societe).filter(Societe.active == True).all()
    sirens = {s.siren for s in societes}

    records = json.load(open(filename))
    for record in records:
        if "fields" in record:
            fields = record["fields"]
        else:
            fields = record
        try:
            siren = str(fields["siren"])
            date_radiation = (
                fields.get("date_radiation")
                or fields.get("date_de_radiation")
                or fields.get("date")
            )
        except BaseException:
            continue

        if siren not in sirens:
            continue

        m = toolz.filter(lambda societe: societe.siren == siren, societes)
        m = list(m)

        for societe in m:
            print(
                f"La société {societe.nom} ({societe.site_web}) a été radiée le {date_radiation}"
            )

            societe.active = False

    db.session.commit()


# def main():
#     print(78 * "-")
#     # maj_radiations("imports/entreprises-radiees-2017.json")
#     # maj_radiations("imports/societes-radiees-2019.json")
#     maj_radiations("imports/societes-radiees-2020.json")
#
#     print(78 * "-")
#     importer = ChiffreClefsImporter()
#     # importer.import_file("imports/chiffres-cles-2018.json")
#     importer.import_file("imports/chiffres-cles-2019.json")
#     importer.import_file("imports/chiffres-cles-2020.json")
#     print("{} infos importées / MAJ".format(importer.counter))
#
#     db.session.commit()


# def check_anciens_membres():
#     all_partenaires = Partenaire.query.all()
#     sirens = siren_des_entreprises_radiees()
#     for p in all_partenaires:
#         siren = get_siren(p)
#         radiee = siren in sirens
#         if radiee or p.type_cotisation == "Ancien membre":
#             print(p.nom, radiee, p.type_cotisation)
#
#
# def siren_des_entreprises_radiees():
#     result = set()
#     all_partenaires = Partenaire.query.all()
#     all_sirens = {get_siren(p) for p in all_partenaires}
#
#     for year in range(2017, 2012, -1):
#         filename = "data/entreprises-radiees-{}.json".format(year)
#         records = json.load(open(filename))
#         for record in records:
#             fields = record["fields"]
#             try:
#                 siren = str(fields["siren"])
#             except BaseException:
#                 continue
#
#             if siren not in all_sirens:
#                 continue
#             result.add(siren)
#     return result


# class ChiffreClefsImporter(object):
#     def __init__(self):
#         self.counter = 0
#         self.all_partenaires = Partenaire.query.all()  # type: List[Partenaire]
#         self.all_sirens = {get_siren(p) for p in self.all_partenaires}
#
#     def import_file(self, filename: str):
#         with open(filename, "rb") as jsonfile:
#             objects = ijson.items(jsonfile, "item.fields")
#             for obj in objects:
#                 siren = obj.get("siren")
#                 if not siren:
#                     continue
#                 if siren not in self.all_sirens:
#                     continue
#
#                 # pprint(obj)
#                 self.import_object(obj)
#
#     def import_object(self, obj: Dict):
#         siren = obj["siren"]
#         denomination = obj["denomination"]
#         cp = obj.get("num_dept")
#         code_ape = obj.get("code_ape")
#         ville = obj.get("ville")
#
#         matches = toolz.filter(lambda p: get_siren(p) == siren, self.all_partenaires)
#         partenaires = list(matches)  # type: List[Partenaire]
#         assert partenaires
#
#         for partenaire in partenaires:
#             partenaire.denomination = denomination
#
#             if not partenaire.pays == "FR":
#                 print(f"{partenaire.nom}: pays = {partenaire.pays} -> FR")
#                 partenaire.pays = "FR"
#
#             if not partenaire.ville:
#                 print(f"{partenaire.nom}: ville = {partenaire.ville} -> {ville}")
#                 partenaire.ville = ville
#
#             # if cp != p.code_postal and not cp.endswith('000'):
#             if not partenaire.code_postal:
#                 print(f"{partenaire.nom}: CP = {partenaire.code_postal} -> {cp}")
#                 partenaire.code_postal = cp
#
#             if code_ape and (partenaire.code_ape != code_ape):
#                 print(f"{partenaire.nom}: APE = {partenaire.code_ape} -> {code_ape}")
#                 partenaire.code_ape = code_ape
#
#             for millesime in [1, 2, 3]:
#                 if f"millesime_{millesime}" not in obj:
#                     continue
#
#                 year = int(obj[f"millesime_{millesime}"])
#                 ca = get_ca(obj, f"ca_{millesime}")
#                 effectif = get_int(obj, f"effectif_{millesime}")
#                 resultat = get_ca(obj, f"resultat{millesime}")
#
#                 self.set_info(partenaire, year, "business", "ca", ca)
#                 self.set_info(partenaire, year, "business", "resultat", resultat)
#                 self.set_info(partenaire, year, "rh", "effectif", effectif)
#
#     def set_info(self, partenaire, year, type, attr, value):
#         # if year != 2017:
#         #     return
#
#         if not value:
#             return
#
#         if type == "business":
#             infos = partenaire.business_infos
#         elif type == "rh":
#             infos = partenaire.rh_infos
#         else:
#             raise RuntimeError
#
#         is_new = False
#         for info in infos:
#             if info.year == year:
#                 break
#         else:
#             is_new = True
#             if type == "business":
#                 info = PartenaireBusinessInfo(year=year)
#             else:
#                 info = PartenaireRHInfo(year=year)
#
#         old_value = getattr(info, attr, None)
#         if value != old_value:
#             print(
#                 "{}, year: {}, attr: {}, old: {}, new: {}".format(
#                     partenaire.nom, year, attr, old_value, value
#                 )
#             )
#             setattr(info, attr, value)
#
#             self.counter += 1
#
#         if is_new:
#             infos.append(info)
#
#
# def get_siren(p):
#     if not p.siret or len(p.siret) != 14:
#         return None
#     return p.siret[0:9]
#
#
# def get_int(obj, key):
#     return int(obj.get(key, "0"))
#
#
# def get_ca(obj, key):
#     return int(round(int(obj.get(key, "0")) / 1000.0))
