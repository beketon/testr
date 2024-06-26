"""add field for uniqe

Revision ID: 4d2546fd0d84
Revises: 0e9d36a03900
Create Date: 2024-02-25 19:34:24.158166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d2546fd0d84'
down_revision: Union[str, None] = '0e9d36a03900'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'directions', ['transportation_type'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'directions', type_='unique')
    # ### end Alembic commands ###
