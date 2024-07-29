from pagic import Page

from .._common import make_count


class RegionsPage(Page):
    menu = "main"
    menu_order = 20

    name = "regions"
    path = "/regions/"

    def context(self):
        count = make_count("regions")
        return {
            "title": "Annuaire par région",
            "regions": count,
        }
