"""empty message

Revision ID: 60be936e0b88
Revises: b71bd66deabe
Create Date: 2022-08-09 10:19:44.498042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "60be936e0b88"
down_revision = "b71bd66deabe"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_solution_slug"), "solution", ["slug"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_solution_slug"), table_name="solution")
    # ### end Alembic commands ###