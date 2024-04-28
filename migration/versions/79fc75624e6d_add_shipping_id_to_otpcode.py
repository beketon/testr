"""add shipping_id to otpcode

Revision ID: 79fc75624e6d
Revises: 466ad4589201
Create Date: 2024-02-07 16:14:05.090904

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '79fc75624e6d'
down_revision: Union[str, None] = '466ad4589201'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'otp_signing_code',
        sa.Column(
            'shipping_id',
            sa.Integer(),
            nullable=True))
    op.create_foreign_key(None, 'otp_signing_code', 'shipping', ['shipping_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'otp_signing_code', type_='foreignkey')
    op.drop_column('otp_signing_code', 'shipping_id')
    # ### end Alembic commands ###