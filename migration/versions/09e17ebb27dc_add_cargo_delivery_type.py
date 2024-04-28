"""add cargo delivery type

Revision ID: 09e17ebb27dc
Revises: 54b2d2b0fcf4
Create Date: 2024-02-02 00:06:39.686625

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '09e17ebb27dc'
down_revision: Union[str, None] = '54b2d2b0fcf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    cargo_pickup_type = postgresql.ENUM('DELIVERY', 'PICKUP', name='deliverytype')
    cargo_pickup_type.create(op.get_bind())
    op.add_column('orders', sa.Column('cargo_pickup_type', postgresql.ENUM('DELIVERY', 'PICKUP', name='deliverytype'), server_default='PICKUP', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'cargo_pickup_type')
    # ### end Alembic commands ###