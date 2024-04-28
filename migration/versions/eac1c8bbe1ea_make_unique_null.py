"""make unique null

Revision ID: eac1c8bbe1ea
Revises: 4d2546fd0d84
Create Date: 2024-02-25 20:14:25.254013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eac1c8bbe1ea'
down_revision: Union[str, None] = '4d2546fd0d84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('directions', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('directions', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('directions', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('directions', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
