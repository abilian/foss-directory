"""
!!!
Copy/pasted from the original corpologia project.
!!!
"""

import json

from sqlalchemy import Column, Integer, String

from app.models.base import Base

__all__ = [
    "SireneUniteLegale",
    "SireneEtablissement",
    "PoleEmploiEtablissement",
    "PoleEmploiAnnonce",
    "Page",
]


class JsonMixin:
    json: str

    @property
    def _json(self):
        return json.loads(self.json)


class SireneUniteLegale(JsonMixin, Base):
    __tablename__ = "sirene_unitelegale"

    siren = Column(String, primary_key=True)
    denomination = Column(String, index=True)
    json = Column(String, default="{}", nullable=False)


class SireneEtablissement(JsonMixin, Base):
    __tablename__ = "sirene_etablissement"

    siret = Column(String, primary_key=True)
    siren = Column(String, index=True, nullable=False)
    json = Column(String, default="{}", nullable=False)


class PoleEmploiEtablissement(JsonMixin, Base):
    __tablename__ = "pe_etablissement"

    siret = Column(String, primary_key=True)
    siren = Column(String, index=True, nullable=False)
    json = Column(String, default="{}", nullable=False)


class PoleEmploiAnnonce(JsonMixin, Base):
    __tablename__ = "pe_annonce"

    id = Column(String, primary_key=True)
    json = Column(String, default="{}", nullable=False)


class Page(Base):
    __tablename__ = "crawl_page"

    url = Column(String, primary_key=True)
    domain = Column(String, default="", nullable=False, index=True)

    status = Column(Integer, default=0, nullable=False)
    content_type = Column(String, default="", nullable=False)
    lang = Column(String, default="", nullable=False)

    # Depth from the home page
    depth = Column(Integer, default=0, nullable=False)

    html = Column(String, default="", nullable=False)
    text = Column(String, default="", nullable=False)

    _json = Column(String, default="{}", nullable=False)
