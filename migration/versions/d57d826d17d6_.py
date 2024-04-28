"""empty message

Revision ID: d57d826d17d6
Revises: 2eb57c37803b, 55c87e7d787e, bd246bca9ba1, d6c4ecbf781e, dae87cf5cfd3
Create Date: 2024-03-06 00:51:46.948113

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd57d826d17d6'
down_revision: Union[str, None] = ('2eb57c37803b', '55c87e7d787e', 'bd246bca9ba1', 'd6c4ecbf781e', 'dae87cf5cfd3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
