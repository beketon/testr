"""added field is_loaded to Shipping

Revision ID: 1094ac76b4b4
Revises: 7cabd012a01f
Create Date: 2024-04-07 06:06:47.969674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1094ac76b4b4'
down_revision: Union[str, None] = '7cabd012a01f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shipping', sa.Column('is_loaded', sa.Boolean(), server_default=sa.text('false'), nullable=True))


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shipping', 'is_loaded')
    # ### end Alembic commands ###
