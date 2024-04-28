"""dont make unique group name

Revision ID: b9270f78c2a5
Revises: d781aab01736
Create Date: 2024-03-18 01:04:47.791229

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b9270f78c2a5'
down_revision: Union[str, None] = 'd781aab01736'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column('fastapi_auth_group', 'name_ru',
    #                 existing_type=sa.VARCHAR(length=150),
    #                 nullable=True,
    #                 existing_comment='group name in English')
    op.drop_index('ix_fastapi_auth_group_name', table_name='fastapi_auth_group')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_fastapi_auth_group_name', 'fastapi_auth_group', ['name'], unique=True)
    op.alter_column('fastapi_auth_group', 'name_ru',
                    existing_type=sa.VARCHAR(length=150),
                    nullable=False,
                    existing_comment='group name in English')
    # ### end Alembic commands ###