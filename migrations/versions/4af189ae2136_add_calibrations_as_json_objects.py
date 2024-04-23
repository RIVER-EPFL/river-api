"""Add calibrations as JSON objects

Revision ID: 4af189ae2136
Revises: 4ccae82ccb31
Create Date: 2024-04-18 17:13:55.594698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4af189ae2136'
down_revision: Union[str, None] = '4ccae82ccb31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_sensorcalibration_calibrated_on', table_name='sensorcalibration')
    op.drop_index('ix_sensorcalibration_id', table_name='sensorcalibration')
    op.drop_index('ix_sensorcalibration_iterator', table_name='sensorcalibration')
    op.drop_table('sensorcalibration')
    op.add_column('sensor', sa.Column('calibrations', sa.JSON(), nullable=True))
    op.alter_column('sensor', 'parameter_id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sensor', 'parameter_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('sensor', 'calibrations')
    op.create_table('sensorcalibration',
    sa.Column('calibrated_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('sensor_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('slope', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('intercept', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('min_range', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('max_range', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('iterator', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensor.id'], name='sensorcalibration_sensor_id_fkey'),
    sa.PrimaryKeyConstraint('iterator', name='sensorcalibration_pkey'),
    sa.UniqueConstraint('id', name='sensorcalibration_id_key')
    )
    op.create_index('ix_sensorcalibration_iterator', 'sensorcalibration', ['iterator'], unique=False)
    op.create_index('ix_sensorcalibration_id', 'sensorcalibration', ['id'], unique=False)
    op.create_index('ix_sensorcalibration_calibrated_on', 'sensorcalibration', ['calibrated_on'], unique=False)
    # ### end Alembic commands ###
