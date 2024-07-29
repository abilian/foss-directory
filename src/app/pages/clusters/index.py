from pagic import Page

from app.extensions import db
from app.models import Societe
from app.models.cluster import Cluster, societe_to_cluster


class ClustersPage(Page):
    name = "clusters"
    menu = "main"
    menu_order = 30

    path = "/clusters/"
    label = "Clusters membres du CNLL"

    def context(self):
        clusters = db.session.query(Cluster).all()
        counter = []
        for cluster in clusters:
            stmt = Societe.get_base_select()
            stmt = (
                stmt.join(societe_to_cluster)
                .where(societe_to_cluster.c.cluster_id == cluster.id)
                .where(societe_to_cluster.c.societe_siren == Societe.siren)
            )
            result = db.session.execute(stmt)
            societes: list[Societe] = list(result.scalars())
            counter.append((len(societes), cluster))

        counter.sort(reverse=True)

        return {
            "clusters": counter,
        }
