from pagic import Page

from .._common import get_societes
from .index import VillesPage


class VillePage(Page):
    name = "ville"
    path = "/villes/<ville>"
    parent = VillesPage

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
