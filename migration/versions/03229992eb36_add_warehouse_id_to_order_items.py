"""add warehouse_id to order_items

Revision ID: 03229992eb36
Revises: 4356f6ee170d
Create Date: 2024-01-31 11:28:37.991687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03229992eb36'
down_revision: Union[str, None] = '4356f6ee170d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_items', sa.Column('warehouse_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order_items', 'warehouses', ['warehouse_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order_items', type_='foreignkey')
    op.drop_column('order_items', 'warehouse_id')
    # ### end Alembic commands ###
