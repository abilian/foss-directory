import json
import re
import time
from datetime import datetime
from pprint import pformat

import click
import requests
from devtools import debug
from flask.cli import with_appcontext
from functional import seq
from tqdm import tqdm

from app.extensions import db
from app.models import Etablissement, PoleEmploiAnnonce

CLIENT_ID = (
    "PAR_sandbox_c10bd6635a35ff70f97dab0cdf271ed7f73e6393335f757d206147c645a75b4f"
)
SECRET_KEY = "90a49365e8fe8d4499c412a71221ad4a00f49b8540cbb05526f8f3906ccc7b60"

KEYWORDS = [
    "linux",
    "python",
    "java",
    "javascript",
    "debian",
    "ubuntu",
    "scrum",
    "freebsd",
    "kubernetes",
    "ocaml",
    "blockchain",
    "saas",
    "paas",
    "reactjs",
    "angularjs",
    "vuejs",
    "j2ee",
    "symfony",
    "jquery",
    "scikit",
    "rhel",
    "ubuntu",
    "docker",
]

ROME = {}

for line in open("config/rome_keep.txt").readlines():
    code, label = line.strip().split(" ", 1)
    ROME[code] = label

ROME_CODES = set(ROME.keys())


def register(cli):
    cli.add_command(pe)


@click.group("pole-emploi")
def pe():
    "Import data from Pole Emploi"
    pass


@pe.command("fetch")
@with_appcontext
def fetch_offres():
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(f"## {date_time}")

    client = Client()
    client.connect()

    criterias = {
        "publieeDepuis": 1,
        # "romeProfessionCardCode": "M1805",
        # "keywords": "linux"
    }
    client.fetch_offres(criterias)

    # token = get_token()
    # # print(78 * "#")
    # # print_offres(token)
    # print(78 * "#")
    # print_entreprises(token)


@pe.command("fetch-more")
@with_appcontext
def fetch_more():
    client = Client()
    client.connect()

    for rome_code, rome_label in ROME.items():
        print(f"# Fetching job for ROME label: {rome_label}")
        criterias = {
            "romeProfessionCode": rome_code,
        }
        client.fetch_offres(criterias)
        print()
        print()


class Client:
    token: str

    def connect(self):
        url0 = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": SECRET_KEY,
            "scope": f"api_offresdemploiv1 o2dsoffre api_pagesentreprisesv1 "
            f"pagesentreprises application_{CLIENT_ID}",
        }
        res = requests.post(url0, headers=headers, data=data)
        if not res.ok:
            print(res)
            print(res.text)
            raise RuntimeError

        print("Connected")

        token = res.json()["access_token"]
        self.token = token

    def fetch_offres(self, criterias):
        url = "https://api.emploi-store.fr/partenaire/offresdemploi/v1/rechercheroffres"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        query_params = {
            "technicalParameters": {"page": 1, "per_page": 100, "sort": 1},
            "criterias": criterias,
        }

        count = 0
        for i in range(0, 10):
            print(f"page: {i}")
            res = requests.post(url, headers=headers, json=query_params)
            if not res.ok:
                db.session.commit()
                print(f"Done: {count} added")
                return

            res_json = res.json()
            results = res_json["results"]
            for r in results:
                id = r["offerId"]
                title = r.get("title", "")

                code_rome = r.get("romeProfessionCode")
                if code_rome not in ROME_CODES:
                    continue

                if db.session.query(PoleEmploiAnnonce).get(id):
                    continue

                annonce = PoleEmploiAnnonce(id=id)
                annonce.json = json.dumps(r)
                db.session.add(annonce)
                print(f"Adding: {id}: {title}")
                count += 1

            db.session.commit()

            query_params["technicalParameters"]["page"] += 1
            time.sleep(2)

        print(f"Done: {count} added")


@pe.command("dump-rome")
@with_appcontext
def dump_rome():
    offres = db.session.query(PoleEmploiAnnonce).all()
    # l = []
    for offre in offres:
        d = json.loads(offre.json)
        rome_code = d.get("romeProfessionCode")
        rome_name = d.get("romeProfessionName")
        print(rome_code, rome_name)
        if not rome_code:
            continue
        # l.append((rome_code, rome_name))
    # counter = Counter(l)
    # pprint(counter.most_common())


@pe.command("filter")
@click.option("--limit")
@with_appcontext
def filter(limit=0):
    query = db.session.query(PoleEmploiAnnonce)
    if limit:
        query = query.limit(limit)
    jobs: list[PoleEmploiAnnonce] = query.all()

    for job in jobs:
        record = json.loads(job.json)
        rome_code = record.get("romeProfessionCode", "xxxxx")
        rome_name = record.get("romeProfessionName", "yyy")

        description = record.get("description", "").lower()

        words_list = re.findall(r"(\w[\w']*\w|\w)", description)
        words_set = set(words_list)

        keywords = set(KEYWORDS).intersection(words_set)
        if keywords:
            print(f"# ROME: {rome_code} {rome_name}")
            print(f"keywords: {', '.join(list(keywords))}")
            print("title:", record.get("title"))
            print("company:", record.get("companyName"))
            print()


@pe.command()
@click.option("--limit")
@with_appcontext
def cleanup(limit=0):
    query = db.session.query(PoleEmploiAnnonce)
    if limit:
        query = query.limit(limit)
    jobs: list[PoleEmploiAnnonce] = query.all()

    for i, job in tqdm(enumerate(jobs)):
        record = json.loads(job.json)
        rome_code = record.get("romeProfessionCode", "xxxxx")
        record.get("title")
        if rome_code not in ROME_CODES:
            # print(f"removing: {title}")
            db.session.delete(job)
        else:
            pass
            # print(f"keeping: {title}")

        if i % 100 == 0:
            db.session.commit()

    db.session.commit()


###
@pe.command("entreprises")
@with_appcontext
def print_entreprises():
    client = Client()
    client.connect()

    token = client.token
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    output = open("entreprises.log", "w")
    url = "https://api.emploi-store.fr/partenaire/pagesentreprises/v1/pagesentreprises/{siret}"

    sirets = seq(db.session.query(Etablissement.siret).all()).flatten().to_set()

    for siret in sirets:
        time.sleep(4)
        siret = siret.strip()
        print(siret)
        output.write(f"# {siret}\n")

        res = requests.get(url.format(siret=siret), headers=headers)
        if res.ok:
            output.write(pformat(res.json()) + "\n")
            debug(res.json())
