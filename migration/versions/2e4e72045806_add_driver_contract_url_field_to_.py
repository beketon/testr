"""add driver_contract_url field to Shipping

Revision ID: 2e4e72045806
Revises: ae012a494022
Create Date: 2024-03-23 05:37:36.466368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e4e72045806'
down_revision: Union[str, None] = 'ae012a494022'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'driver_contract_url')
    op.add_column('shipping', sa.Column('driver_contract_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shipping', 'driver_contract_url')
    op.add_column('orders', sa.Column('driver_contract_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
