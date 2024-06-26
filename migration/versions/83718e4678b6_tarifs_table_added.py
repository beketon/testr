"""Tarifs table added

Revision ID: 83718e4678b6
Revises: d57d826d17d6
Create Date: 2024-03-06 00:59:14.382563

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '83718e4678b6'
down_revision: Union[str, None] = 'd57d826d17d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'tarifs', sa.Column(
            'id', sa.Integer(), nullable=False), sa.Column(
            'calculation_type', postgresql.ENUM(
                'VOLUME', 'WEIGHT', 'HANDLING', 'DELIVERY_WEIGHT', 'DELIVERY_VOLUME', 'SENDER_CARGO_PICKUP_VOLUME', 'SENDER_CARGO_PICKUP_WEIGHT', name='calculationtype'), nullable=False), sa.Column(
                    'direction_id', sa.Integer(), nullable=False), sa.Column(
                        'amount', sa.Integer(), nullable=False), sa.Column(
                            'price', sa.Float(), nullable=False), sa.ForeignKeyConstraint(
                                ['direction_id'], ['directions.id'], ), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint(
                                    'calculation_type', 'direction_id', 'amount', name='idx_tarifs_calculation_type_direction_id_amount'))
    op.create_index(op.f('ix_tarifs_id'), 'tarifs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tarifs_id'), table_name='tarifs')
    op.drop_table('tarifs')
    # ### end Alembic commands ###
