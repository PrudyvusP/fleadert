"""empty message

Revision ID: b3ad49efe662
Revises: 90795f61286a
Create Date: 2020-11-09 18:07:19.491699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3ad49efe662'
down_revision = '90795f61286a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('executed_number', sa.String(length=30), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'executed_number')
    # ### end Alembic commands ###
