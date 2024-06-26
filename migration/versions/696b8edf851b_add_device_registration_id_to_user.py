"""add device_registration_id to user

Revision ID: 696b8edf851b
Revises: 79fc75624e6d
Create Date: 2024-02-08 03:37:31.656704

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '696b8edf851b'
down_revision: Union[str, None] = '79fc75624e6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'users',
        sa.Column(
            'device_registration_id',
            sa.String(),
            nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'device_registration_id')
    # ### end Alembic commands ###
