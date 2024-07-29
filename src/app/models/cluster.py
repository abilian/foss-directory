from __future__ import annotations

from functools import total_ordering

import sqlalchemy as sa
from sqlalchemy import JSON, Column, ForeignKey, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy_utils import URLType

from app.models import Base, Societe

societe_to_cluster = sa.Table(
    "societe_to_cluster",
    Base.metadata,
    Column("societe_siren", String, ForeignKey("societe.siren")),
    Column("cluster_id", String, ForeignKey("cluster.id", onupdate="cascade")),
)


@total_ordering
class Cluster(Base):
    __tablename__ = "cluster"

    id = Column(String, primary_key=True)
    nom = Column(String, default="", nullable=False)
    site_web = Column(URLType, default="", nullable=False)
    logo = Column(String, default="", nullable=False)
    description = Column(String, default="", nullable=False)

    _json = deferred(Column(JSON, default={}, server_default="{}", nullable=False))

    societes = relationship(Societe, secondary=societe_to_cluster, backref="clusters")

    def __repr__(self):
        return f"<Cluster {self.nom}>"

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id
