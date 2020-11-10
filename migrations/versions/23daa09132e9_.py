"""empty message

Revision ID: 23daa09132e9
Revises: b3ad49efe662
Create Date: 2020-11-09 18:17:58.686502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23daa09132e9'
down_revision = 'b3ad49efe662'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('executor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'users', ['executor_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'executor_id')
    # ### end Alembic commands ###
