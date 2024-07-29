from pagic import Page

from app.pages._common import get_societes, make_count


class RegionPage(Page):
    name = "region"
    path = "/<region>/"

    def context(self):
        region = self.args["region"]

        societes = get_societes()
        societes = [s for s in societes if region in s.regions]

        return {
            "title": f"Annuaire de la région: {region}",
            "societes": societes,
        }


class RegionsPage(Page):
    name = "regions"
    menu = "main"
    path = "/regions/"
    children = [RegionPage]

    def context(self):
        count = make_count("regions")
        return {
            "title": "Annuaire par région",
            "regions": count,
        }
