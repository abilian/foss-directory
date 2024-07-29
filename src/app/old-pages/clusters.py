from pagic import Page, url_for
from sqlalchemy import select

from app.extensions import db
from app.models import Societe
from app.models.cluster import Cluster, societe_to_cluster


class ClusterPage(Page):
    name = "cluster"
    path = "/<cluster>/"
    template = "pages/cluster.j2"

    def context(self):
        cluster_id = self.args["cluster"]
        cluster = db.session.query(Cluster).get(cluster_id)

        stmt = (
            select(Societe)
            .join(societe_to_cluster)
            .where(societe_to_cluster.c.cluster_id == cluster.id)
            .where(societe_to_cluster.c.societe_siren == Societe.siren)
            .order_by(Societe.nom)
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


class ClustersPage(Page):
    name = "clusters"
    path = "/clusters/"
    menu = "main"
    children = [ClusterPage]
    label = "Clusters membres du CNLL"

    def context(self):
        clusters = db.session.query(Cluster).all()
        counter = []
        for cluster in clusters:
            counter.append((len(cluster.societes), cluster))

        counter.sort(reverse=True)

        return {
            "clusters": counter,
        }
