from pagic import Page

from .._common import make_count


class VillesPage(Page):
    menu = "main"
    menu_order = 10

    name = "villes"
    path = "/villes/"

    def context(self):
        count = make_count("villes")
        return {
            "title": "Annuaire par ville",
            "villes": count,
        }
