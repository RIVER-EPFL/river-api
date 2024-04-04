"""Add sensor parameters

Revision ID: 8e9e0ccad3c3
Revises: af1563ce9135
Create Date: 2024-04-04 12:55:04.391091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8e9e0ccad3c3'
down_revision: Union[str, None] = 'af1563ce9135'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensorparameter',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('acronym', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('unit', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('iterator', sa.Integer(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('iterator'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_sensorparameter_acronym'), 'sensorparameter', ['acronym'], unique=False)
    op.create_index(op.f('ix_sensorparameter_id'), 'sensorparameter', ['id'], unique=False)
    op.create_index(op.f('ix_sensorparameter_iterator'), 'sensorparameter', ['iterator'], unique=False)
    op.create_index(op.f('ix_sensorparameter_name'), 'sensorparameter', ['name'], unique=False)
    op.create_index(op.f('ix_sensorparameter_unit'), 'sensorparameter', ['unit'], unique=False)
    op.drop_column('sensor', 'parameter_unit')
    op.drop_column('sensor', 'parameter_acronym')
    op.drop_column('sensor', 'parameter_name')
    op.drop_column('sensor', 'parameter_db_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensor', sa.Column('parameter_db_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('sensor', sa.Column('parameter_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('sensor', sa.Column('parameter_acronym', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('sensor', sa.Column('parameter_unit', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_sensorparameter_unit'), table_name='sensorparameter')
    op.drop_index(op.f('ix_sensorparameter_name'), table_name='sensorparameter')
    op.drop_index(op.f('ix_sensorparameter_iterator'), table_name='sensorparameter')
    op.drop_index(op.f('ix_sensorparameter_id'), table_name='sensorparameter')
    op.drop_index(op.f('ix_sensorparameter_acronym'), table_name='sensorparameter')
    op.drop_table('sensorparameter')
    # ### end Alembic commands ###
