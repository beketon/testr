"""add is_direction_user to User

Revision ID: 08b041238e00
Revises: d64bf7575a87
Create Date: 2024-03-17 22:39:28.573994

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '08b041238e00'
down_revision: Union[str, None] = 'd64bf7575a87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'users',
        sa.Column(
            'is_direction_user',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=True,
            comment='Is it a direction user'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_direction_user')
    # ### end Alembic commands ###