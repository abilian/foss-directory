from __future__ import annotations

from flask import current_app, jsonify, redirect, url_for
from pydantic import BaseModel

from app.extensions import db
from app.models import Societe

from . import route


class SolutionDTO(BaseModel):
    id: str
    name: str
    wikidata_id: str
    description: str

    class Config:
        orm_mode = True


class EtablissementDTO(BaseModel):
    siret: str
    adresse: str
    region: str
    ville: str
    lnglat: list

    class Config:
        orm_mode = True


class SocieteDTO(BaseModel):
    siren: str
    nom: str
    denomination_insee: str
    site_web: str
    domain: str
    active: bool
    description: str
    naf_code: str

    ville: str
    region: str
    clusters: list[str]
    topics: list
    tags: list[str]
    tagline: str

    # insee: Dict[str, Any]

    solutions: list[SolutionDTO]
    etablissements: list[EtablissementDTO]

    effectifs: str

    class Config:
        orm_mode = True


@route("/societes/<siren>/")
def societe(siren):
    societe: Societe = db.session.query(Societe).get(siren)
    societe_dto = SocieteDTO.from_orm(societe).dict()
    return jsonify(societe=societe_dto)


@route("/societes/<siren>/screenshot")
def screenshot_societe(siren):
    societe: Societe = db.session.query(Societe).get(siren)
    config = current_app.config
    if societe.screenshot_id:
        url = f"{config['S3_PUBLIC_URL']}/{societe.screenshot_id}"
        return redirect(url)
    else:
        return redirect(url_for("static", filename="img/question-mark.png"))
