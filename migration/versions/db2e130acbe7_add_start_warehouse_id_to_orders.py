"""add start warehouse id to orders

Revision ID: db2e130acbe7
Revises: 71583b6c8030
Create Date: 2024-03-28 11:49:34.168021

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'db2e130acbe7'
down_revision: Union[str, None] = '71583b6c8030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('start_warehouse_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'orders', 'warehouses', ['start_warehouse_id'], ['id'])
    op.drop_column('users', 'salary')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('salary', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.drop_column('orders', 'start_warehouse_id')
    # ### end Alembic commands ###
