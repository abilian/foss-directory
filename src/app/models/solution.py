from __future__ import annotations

from functools import total_ordering
from typing import Any

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import deferred
from sqlalchemy_json import NestedMutableJson

from app.models.base import Base
from app.models.util import make_tagline
from app.util import html_to_text

__all__ = ["Solution"]


@total_ordering
class Solution(Base):
    __tablename__ = "solution"

    id = Column(Integer, primary_key=True)
    old_id = Column(String)

    #: Shown only if true
    active = Column(Boolean, default=False)

    #: Public name
    name = Column(String)

    slug = Column(String, index=True, unique=True)

    # Links / external ids
    home_url = Column(String, default="")
    wikipedia_fr_url = Column(String, default="")
    wikipedia_en_url = Column(String, default="")

    # External ids
    wikidata_id = Column(String, default="", nullable=False)
    cdl_id = Column(Integer)
    afs_id = Column(String)
    sill_id = Column(Integer)

    #
    wikidata = Column(JSONB, default={})

    #: Description as text (not used)
    description_txt = Column(String, default="", nullable=False, server_default="")

    #: Description (html)
    description = Column(String, default="", nullable=False)

    # Images
    screenshot_id = Column(String, default="")
    logo_id = Column(String, default="")

    # Schemaless properties
    _props = deferred(Column(NestedMutableJson))
    _json = deferred(Column(NestedMutableJson))

    def __repr__(self):
        return f"<Solution {self.name}>"

    @property
    def description_as_text(self):
        return html_to_text(self.description)

    @property
    def tagline(self):
        return make_tagline(self.description_as_text)

    @property
    def aliases(self) -> set:
        return set(self._json.get("aliases", []))

    def add_alias(self, alias):
        aliases = self.aliases
        aliases.add(alias)
        self._json["aliases"] = list(aliases)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def prop_get(self, key: str, default: Any = None):
        if not self._props:
            return default
        return self._props.get(key, default)

    def prop_set(self, key: str, value: Any):
        if self._props is None:
            self._props = {}
        self._props[key] = value

    @property
    def sill_data(self) -> dict:
        return self._json.get("sill", {})

    @property
    def sill_name(self) -> dict:
        return self.sill_data.get("name")

    # @property
    # def wikidata_data(self) -> dict:
    #     return self.sill_data.get("wikidataData", {})
    #
    # @property
    # def source_url(self):
    #     return self.get(["wikidata", "sourceUrl"])
    #
    # @property
    # def license(self):
    #     return self.get(["wikidata", "license"])
    #
    # def get(self, keys: list) -> Any:
    #     """
    #     Get a value from the nested json dict
    #     """
    #     if len(keys) == 1:
    #         return
    #         return self.wikidata.get(keys[0])
