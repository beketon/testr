"""add middle_name

Revision ID: 220bb53c8e6e
Revises: cb536e4a86ea
Create Date: 2024-01-24 03:37:50.712798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '220bb53c8e6e'
down_revision: Union[str, None] = 'cb536e4a86ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'shipping', 'users', ['driver_id'], ['id'], use_alter=True)
    op.add_column('users', sa.Column('middle_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('district_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('car_engine_volume', sa.Float(), nullable=True))
    op.create_foreign_key(None, 'users', 'districts', ['district_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'car_engine_volume')
    op.drop_column('users', 'district_id')
    op.drop_column('users', 'middle_name')
    op.drop_constraint(None, 'shipping', type_='foreignkey')
    # ### end Alembic commands ###
