from __future__ import annotations

import webargs.flaskparser
from flask import jsonify
from pydantic import BaseModel
from sqlalchemy import func, text

from app.extensions import db
from app.models import Etablissement
from app.models import Societe as SocieteORM

from . import route


class Societe(BaseModel):
    siren: str
    nom: str
    description: str

    ville: str
    region: str
    clusters: list[str]
    tags: list[str]

    class Config:
        orm_mode = True


pagination_args = {
    "page": webargs.fields.Int(load_default=1),
    "results": webargs.fields.Int(),
    "q": webargs.fields.Str(load_default=""),
    "metier": webargs.fields.Str(load_default=""),
    "cluster": webargs.fields.Str(load_default=""),
    "region": webargs.fields.Str(load_default=""),
    "ville": webargs.fields.Str(load_default=""),
}


@route("/societes/")
@webargs.flaskparser.use_args(pagination_args, location="query")
def societes(args):
    query = db.session.query(SocieteORM).filter(SocieteORM.active == True)
    total = query.count()

    query = query.order_by(SocieteORM.nom)

    q = args["q"].lower()
    if q:
        query = query.filter(func.lower(SocieteORM.nom).like(f"%{q}%"))

    region = args["region"]
    if region:
        clause = text("_regions @> to_jsonb((:region)::text)").bindparams(region=region)
        query = query.filter(clause)

    metier = args["metier"]
    if metier:
        query = query.filter(SocieteORM.metier == metier)

    total = query.count()

    page = args["page"]
    query = query.offset((page - 1) * 24).limit(24)

    societes: list[Societe] = query.all()

    societes_dto = [Societe.from_orm(s).dict() for s in societes]
    return jsonify(societes=societes_dto, total=total)


@route("/societes2/")
@webargs.flaskparser.use_args(pagination_args, location="query")
def societes2(args):
    query = (
        db.session.query(SocieteORM)
        .filter(SocieteORM.active == True)
        .order_by(SocieteORM.nom)
    )
    societes: list[Societe] = query.all()

    def predicate(societe: SocieteORM) -> bool:
        if cluster:
            return cluster in societe.clusters
        if ville:
            return ville in societe.villes
        if region:
            return region in societe.regions
        return True

    cluster = args["cluster"]
    ville = args["ville"]
    region = args["region"]
    societes = [s for s in societes if predicate(s)]

    societes_dto = [Societe.from_orm(s).dict() for s in societes]
    return jsonify(societes=societes_dto)


@route("/mapdata/")
def map():
    etablissements = db.session.query(Etablissement).all()

    etablissements_dto = []
    for etablissement in etablissements:
        if not etablissement.geo_data:
            continue
        coords = etablissement.geo_data["geometry"]["coordinates"]
        societe = etablissement.societe
        dto = {
            "lnglat": (coords[0], coords[1]),
            "nom": societe.nom,
            "siret": etablissement.siret,
            "siren": societe.siren,
        }
        etablissements_dto.append(dto)

    ctx = {"etablissements": etablissements_dto}
    return jsonify(ctx)
