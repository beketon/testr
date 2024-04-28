"""add district_id

Revision ID: 55c87e7d787e
Revises: d1a25275a497
Create Date: 2024-02-20 09:46:10.048722

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '55c87e7d787e'
down_revision: Union[str, None] = 'd1a25275a497'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('district_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'orders', 'districts', ['district_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.drop_column('orders', 'district_id')
    # ### end Alembic commands ###