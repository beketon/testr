"""add relatioship with order and order_items

Revision ID: b38f74241dfe
Revises: dab06b67a4e9
Create Date: 2024-02-08 15:58:52.869231

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b38f74241dfe'
down_revision: Union[str, None] = 'dab06b67a4e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'quantity_of_order_items')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'orders',
        sa.Column(
            'quantity_of_order_items',
            sa.INTEGER(),
            autoincrement=False,
            nullable=True))
    # ### end Alembic commands ###
