"""rename reciever to receiver

Revision ID: 54b2d2b0fcf4
Revises: 040e80d39686
Create Date: 2024-02-01 11:16:32.355659

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '54b2d2b0fcf4'
down_revision: Union[str, None] = '040e80d39686'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('orders', 'reciever_fio',
                    new_column_name='receiver_fio', type_=sa.String())
    op.alter_column('orders', 'reciever_phone',
                    new_column_name='receiver_phone', type_=sa.String())

def downgrade():
    op.alter_column('orders', 'reciever_fio',
                    new_column_name='receiver_fio', type_=sa.String())
    op.alter_column('orders', 'reciever_phone',
                    new_column_name='receiver_phone', type_=sa.String())
