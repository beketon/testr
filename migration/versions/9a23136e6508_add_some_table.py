"""add some table

Revision ID: 9a23136e6508
Revises: 39b110de3b55
Create Date: 2024-01-27 22:52:39.943550

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9a23136e6508'
down_revision: Union[str, None] = '39b110de3b55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'shipping_responds', sa.Column(
            'id', sa.Integer(), nullable=False), sa.Column(
            'driver_id', sa.Integer(), nullable=True), sa.Column(
                'shipping_id', sa.Integer(), nullable=True), sa.Column(
                    'respond_status', postgresql.ENUM(
                        'CANCEL', 'CONFIRMED', 'RESPONDED', 'FINISHED', name='shippingrespondstatus'), nullable=True), sa.Column(
                            'created_at', sa.DateTime(), nullable=True), sa.Column(
                                'updated_at', sa.DateTime(), nullable=True), sa.ForeignKeyConstraint(
                                    ['driver_id'], ['users.id'], ), sa.ForeignKeyConstraint(
                                        ['shipping_id'], ['shipping.id'], ), sa.PrimaryKeyConstraint('id'))
    op.drop_table('shipping_driver_association')
    op.add_column('shipping', sa.Column('driver_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'shipping', 'users', ['driver_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shipping', type_='foreignkey')
    op.drop_column('shipping', 'driver_id')
    op.create_table(
        'shipping_driver_association', sa.Column(
            'shipping_id', sa.INTEGER(), autoincrement=False, nullable=True), sa.Column(
            'driver_id', sa.INTEGER(), autoincrement=False, nullable=True), sa.ForeignKeyConstraint(
                ['driver_id'], ['users.id'], name='shipping_driver_association_driver_id_fkey'), sa.ForeignKeyConstraint(
                    ['shipping_id'], ['shipping.id'], name='shipping_driver_association_shipping_id_fkey'))
    op.drop_table('shipping_responds')
    # ### end Alembic commands ###