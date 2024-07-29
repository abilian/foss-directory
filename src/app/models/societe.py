from __future__ import annotations

import json
import re
from typing import Any

import sqlalchemy as sa
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import deferred, relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base
from .corpologia import Page
from .util import make_tagline

__all__ = [
    "Societe",
    "Etablissement",
]

CATEGORIES_EFFECTIFS = {
    "00": "Aucun salarié",
    "01": "1 ou 2 salariés",
    "02": "3 à 5 salariés",
    "03": "6 à 9 salariés",
    "11": "10 à 19 salariés",
    "12": "20 à 49 salariés",
    "21": "50 à 99 salariés",
    "22": "100 à 199 salariés",
    "31": "200 à 249 salariés",
    "32": "250 à 499 salariés",
    "41": "500 à 999 salariés",
    "42": "1 000 à 1 999 salariés",
    "51": "2 000 à 4 999 salariés",
    "52": "5 000 à 9 999 salariés",
    "53": "10 000 salariés et plus",
    "NN": "Aucun salarié",
    "": "Inconnu",
}


societe_to_solution = sa.Table(
    "societe_to_solution",
    Base.metadata,
    Column("societe_siren", String, ForeignKey("societe.siren"), nullable=False),
    Column(
        "solution_id",
        Integer,
        ForeignKey("solution.id", onupdate="cascade"),
        nullable=False,
    ),
)


class Societe(Base):
    __tablename__ = "societe"

    siren = Column(String, primary_key=True)
    nom = Column(String, default="", nullable=False)

    denomination_insee = Column(String, default="", nullable=False)

    # Vrai si la société est en activité
    active = Column(Boolean, default=False, nullable=False)

    site_web = Column(String, default="", nullable=False)
    site_web_down = Column(
        Boolean, default=False, server_default="false", nullable=False
    )
    domain = Column(String, default="", nullable=False)

    screenshot_id = Column(String, default="", nullable=False)
    logo_id = Column(String, default="")

    description = Column(String, default="")
    description_short = Column(String, default="")
    description_long = Column(String, default="")
    metier = Column(String, default="")

    _json = deferred(Column(NestedMutableJson))

    _insee = deferred(Column(String, default="{}", nullable=False))
    _topics = deferred(Column(String, default="[]", nullable=False))
    _entities = deferred(Column(String, default="[]", nullable=False))
    _extra = deferred(Column(String, default="{}", nullable=False))

    # _regions = Column(String, default="")
    _regions = Column(JSONB, default=[])

    # Relations
    solutions = relationship(
        "Solution", secondary=societe_to_solution, backref="societes"
    )
    etablissements = relationship("Etablissement", backref="societe")

    def __repr__(self):
        return f"<Societe {self.nom}>"

    @staticmethod
    def get_base_select():
        return (
            select(Societe)
            .filter(Societe.active == True)
            .filter(Societe.site_web_down == False)
            .order_by(Societe.nom)
        )

    @property
    def topics(self) -> dict[str, Any]:
        return self._decode_json("topics")

    @property
    def insee(self) -> dict[str, Any]:
        return self._decode_json("insee")

    @property
    def entities(self) -> dict[str, Any]:
        return self._decode_json("entities")

    @property
    def tagline(self) -> str:
        return make_tagline(self.description)

    @property
    def tags(self) -> list[str]:
        result = []
        for solution in self.solutions:
            if solution.name:
                m = re.match(r"([^(]+)", solution.name)
                result.append(m.group(1).strip())  # type: ignore
        return result

    def _decode_json(self, key):
        value = getattr(self, "_" + key)
        if not value:
            return []
        else:
            return json.loads(value)

    def _extra_get(self, key, default=None):
        return json.loads(self._extra or "{}").get(key, default)

    def _extra_set(self, key, value):
        extra = json.loads(self._extra or "{}")
        extra[key] = value
        self._extra = json.dumps(extra)

    @property
    def etablissement_principal(self) -> Etablissement | None:
        for etablissement in self.etablissements:
            if etablissement.is_siege:
                return etablissement
        return None

    @property
    def ville(self):
        if self.etablissement_principal:
            return self.etablissement_principal.ville
        else:
            return ""

    @property
    def region(self):
        if self.etablissement_principal:
            return self.etablissement_principal.region
        else:
            return ""

    @property
    def regions(self):
        return {etab.region for etab in self.etablissements if etab.region != "?"}

    @property
    def villes(self):
        return {etab.ville for etab in self.etablissements if etab.ville != "?"}

    @property
    def short_description(self):
        if not self.description:
            return ""
        if len(self.description) > 200:
            return self.description[0:198] + "..."
        else:
            return self.description

    @property
    def effectifs(self) -> str:
        try:
            return CATEGORIES_EFFECTIFS[self.insee["trancheEffectifs"]]
        except:
            return "?"

    @property
    def naf_code(self) -> str:
        return self.insee.get("activitePrincipale", "?????")

    @property
    def pages(self) -> list[Page]:
        from app.extensions import db

        pages = db.session.query(Page).filter(Page.domain == self.domain).all()
        return [page.url for page in pages]

    @property
    def solution_ids(self) -> list[str]:
        return sorted(s.id for s in self.solutions)

    @property
    def date_creation(self) -> str:
        return self.insee.get("dateCreation", "")

    @property
    def naf_libelle(self) -> str:
        # Lazy import because it's slow
        import naf

        return naf.DB.get(self.naf_code, "").description


class Etablissement(Base):
    __tablename__ = "etablissement"

    siret = Column(String, primary_key=True)
    siren = Column(String, ForeignKey(Societe.siren), index=True)

    _json = deferred(Column(JSON, default={}, server_default="{}", nullable=False))

    # societe = relationship(Societe, backref="etablissements")

    _insee = Column(String, default="{}", nullable=False)
    _geo_data = Column(String, default="{}", nullable=False)

    def __repr__(self):
        return f"<Etablissement {self.siret}>"

    @property
    def insee(self) -> dict[str, Any]:
        return self._decode_json("insee")

    @property
    def sirene_data(self) -> dict[str, Any]:
        return self.insee

    @property
    def geo_data(self) -> dict[str, Any]:
        return self._decode_json("geo_data")

    def _decode_json(self, key):
        value = getattr(self, "_" + key)
        if not value:
            return []
        else:
            return json.loads(value)

    @property
    def adresse(self):
        data = self.sirene_data
        adresse = f"{data['numeroVoie']} {data['typeVoie']} {data['libelleVoie']}"
        # if data["complementadresse"]:
        #     adresse += "\n" + data["complementadresse"]
        # adresse += f"\n{data['codepostal']} {data['libellecommune']}"
        return adresse

    @property
    def is_active(self):
        return self.sirene_data["etatAdministratif"] == "A"

    @property
    def is_siege(self):
        return self.sirene_data["etablissementSiege"] == "true"

    @property
    def lnglat(self):
        coords = self.geo_data["geometry"]["coordinates"]
        return [coords[0], coords[1]]

    @property
    def ville(self):
        if not self.geo_data:
            return "?"
        properties = self.geo_data.get("properties")
        if not properties:
            return "?"
        city = properties.get("city")
        return city or "?"

    @property
    def region(self):
        if not self.geo_data:
            return "?"
        properties = self.geo_data.get("properties")
        if not properties:
            return "?"
        context = properties.get("context")
        if not context:
            return "?"
        m = re.match(r"(.*), (.*), (.*) \((.*)\)", context)
        if m:
            return m.group(3)
        m = re.match(r"(.*), (.*), (.*)", context)
        if m:
            return m.group(3)
        return "?"
