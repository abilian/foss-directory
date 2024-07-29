"""empty message

Revision ID: e195da700210
Revises: 
Create Date: 2022-02-01 13:29:58.583166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e195da700210"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cluster",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("site_web", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("_extra", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "crawl_page",
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("lang", sa.String(), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("html", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("_json", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("url"),
    )
    op.create_index(
        op.f("ix_crawl_page_domain"), "crawl_page", ["domain"], unique=False
    )
    op.create_table(
        "pe_annonce",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("json", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pe_etablissement",
        sa.Column("siret", sa.String(), nullable=False),
        sa.Column("siren", sa.String(), nullable=False),
        sa.Column("json", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("siret"),
    )
    op.create_index(
        op.f("ix_pe_etablissement_siren"), "pe_etablissement", ["siren"], unique=False
    )
    op.create_table(
        "sirene_etablissement",
        sa.Column("siret", sa.String(), nullable=False),
        sa.Column("siren", sa.String(), nullable=False),
        sa.Column("json", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("siret"),
    )
    op.create_index(
        op.f("ix_sirene_etablissement_siren"),
        "sirene_etablissement",
        ["siren"],
        unique=False,
    )
    op.create_table(
        "sirene_unitelegale",
        sa.Column("siren", sa.String(), nullable=False),
        sa.Column("denomination", sa.String(), nullable=True),
        sa.Column("json", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("siren"),
    )
    op.create_index(
        op.f("ix_sirene_unitelegale_denomination"),
        "sirene_unitelegale",
        ["denomination"],
        unique=False,
    )
    op.create_table(
        "societe_to_cluster",
        sa.Column("societe_siren", sa.String(), nullable=True),
        sa.Column("cluster_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["cluster_id"], ["cluster.id"], onupdate="cascade"),
        sa.ForeignKeyConstraint(
            ["societe_siren"],
            ["societe.siren"],
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("societe_to_cluster")
    op.drop_index(
        op.f("ix_sirene_unitelegale_denomination"), table_name="sirene_unitelegale"
    )
    op.drop_table("sirene_unitelegale")
    op.drop_index(
        op.f("ix_sirene_etablissement_siren"), table_name="sirene_etablissement"
    )
    op.drop_table("sirene_etablissement")
    op.drop_index(op.f("ix_pe_etablissement_siren"), table_name="pe_etablissement")
    op.drop_table("pe_etablissement")
    op.drop_table("pe_annonce")
    op.drop_index(op.f("ix_crawl_page_domain"), table_name="crawl_page")
    op.drop_table("crawl_page")
    op.drop_table("cluster")
    # ### end Alembic commands ###
