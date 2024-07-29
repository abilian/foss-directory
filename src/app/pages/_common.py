from collections import Counter

import webargs.flaskparser
from sqlalchemy.orm import Query

from app.extensions import db
from app.models import Societe

pagination_args = {
    "page": webargs.fields.Int(load_default=1),
    "results": webargs.fields.Int(),
    "q": webargs.fields.Str(load_default=""),
    "metier": webargs.fields.Str(load_default=""),
    "cluster": webargs.fields.Str(load_default=""),
    "region": webargs.fields.Str(load_default=""),
    "ville": webargs.fields.Str(load_default=""),
}


def get_base_query() -> Query:
    return (
        db.session.query(Societe)
        .filter(Societe.active == True)
        .filter(Societe.site_web_down == False)
        .order_by(Societe.nom)
    )


def get_societes() -> list[Societe]:
    return get_base_query().all()


def make_count(attr) -> list[tuple[str, int]]:
    societes = get_societes()
    counter = Counter()
    for s in societes:
        counter.update(getattr(s, attr))

    count = list(counter.items())

    def sorter(t):
        return (-t[1], t[0])

    count.sort(key=sorter)
    return count


def get_filtered_set(cluster=None, ville=None, region=None) -> list[dict]:
    societes = get_societes()

    def predicate(societe: Societe) -> bool:
        if cluster:
            return cluster in societe.clusters
        if ville:
            return ville in societe.villes
        if region:
            return region in societe.regions
        return True

    return [s for s in societes if predicate(s)]


# def make_vm(societes):
#     class Societe(BaseModel):
#         siren: str
#         nom: str
#         description: str
#
#         ville: str
#         region: str
#         clusters: list[str]
#         tags: list[str]
#
#         class Config:
#             orm_mode = True
#
#     societes_vm = [Societe.from_orm(s).dict() for s in societes]
#     for d in societes_vm:
#         if len(d["description"]) > 300:
#             d["description"] = d["description"][0:300] + "[...]"
#
#     return societes_vm
