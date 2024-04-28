"""add new field is_loaded to OrderItems

Revision ID: f49f442992ef
Revises: b178f237cf1b
Create Date: 2024-04-18 15:44:21.435675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f49f442992ef'
down_revision: Union[str, None] = 'b178f237cf1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_items', sa.Column('is_loaded', sa.Boolean(), server_default=sa.text('false'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_items', 'is_loaded')
    # ### end Alembic commands ###
