from pagic import Page, url_for

from app.extensions import db
from app.models import Societe
from app.models.cluster import Cluster, societe_to_cluster
from app.pages.clusters.index import ClustersPage


class ClusterPage(Page):
    name = "cluster"
    path = "/clusters/<cluster>/"
    parent = ClustersPage

    template = "pages/cluster.j2"

    def context(self):
        cluster_id = self.args["cluster"]
        cluster = db.session.query(Cluster).get(cluster_id)

        stmt = Societe.get_base_select()
        stmt = (
            stmt.join(societe_to_cluster)
            .where(societe_to_cluster.c.cluster_id == cluster.id)
            .where(societe_to_cluster.c.societe_siren == Societe.siren)
        )
        result = db.session.execute(stmt)
        societes: list[Societe] = list(result.scalars())

        return {
            "title": f"Annuaire du cluster: {cluster.nom}",
            "societes": societes,
            "cluster": cluster,
        }


@url_for.register
def url_for_cluster(cluster: Cluster):
    return url_for("cluster", cluster=cluster.id)
