from pagic import Page

from ._common import get_societes, make_count


class VillePage(Page):
    name = "ville"
    path = "/<ville>/"
    # menu = "main"

    def context(self):
        ville = self.args["ville"]

        societes = get_societes()
        societes = [s for s in societes if ville in s.villes]

        title = f"Annuaire du CNLL ({ ville })"
        subtitle = (
            f"Les entreprises du libre et du numérique ouvert de la ville: { ville }"
        )
        return {
            "title": title,
            "subtitle": subtitle,
            "societes": societes,
            "ville": ville,
        }


class VillesPage(Page):
    name = "villes"
    menu = "main"
    path = "/villes/"
    children = [VillePage]

    def context(self):
        count = make_count("villes")
        return {
            "title": "Annuaire par ville",
            "villes": count,
        }
