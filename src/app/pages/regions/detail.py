from pagic import Page

from .._common import get_societes
from .index import RegionsPage


class RegionPage(Page):
    name = "region"
    path = "/regions/<region>/"
    parent = RegionsPage

    def context(self):
        region = self.args["region"]

        societes = get_societes()
        societes = [s for s in societes if region in s.regions]

        return {
            "title": f"Annuaire de la région: {region}",
            "societes": societes,
        }
