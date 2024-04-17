"""Add station data

Revision ID: 3293bb5fb929
Revises: 8e9e0ccad3c3
Create Date: 2024-04-17 09:39:26.072845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3293bb5fb929'
down_revision: Union[str, None] = '8e9e0ccad3c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stationdata',
    sa.Column('iterator', sa.Integer(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('high_resolution', sa.Boolean(), nullable=False),
    sa.Column('last_updated', sa.DateTime(), nullable=False),
    sa.Column('station_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('sensor_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('parameter_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('iterator'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_stationdata_id'), 'stationdata', ['id'], unique=False)
    op.create_index(op.f('ix_stationdata_iterator'), 'stationdata', ['iterator'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stationdata_iterator'), table_name='stationdata')
    op.drop_index(op.f('ix_stationdata_id'), table_name='stationdata')
    op.drop_table('stationdata')
    # ### end Alembic commands ###
