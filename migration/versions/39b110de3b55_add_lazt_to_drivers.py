"""add lazt to drivers

Revision ID: 39b110de3b55
Revises: 2e7eb6cc059c
Create Date: 2024-01-25 02:46:16.729581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39b110de3b55'
down_revision: Union[str, None] = '2e7eb6cc059c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###