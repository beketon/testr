"""add crator to Review

Revision ID: d6c4ecbf781e
Revises: 6f3f8a0a10e1
Create Date: 2024-02-05 11:29:51.282913

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd6c4ecbf781e'
down_revision: Union[str, None] = '6f3f8a0a10e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reviews_driver', sa.Column('creator_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'reviews_driver', 'users', ['creator_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'reviews_driver', type_='foreignkey')
    op.drop_column('reviews_driver', 'creator_id')
    # ### end Alembic commands ###
