"""Remove station position constraint

Revision ID: 66b02583fc42
Revises: 9fd7e97a72af
Create Date: 2024-05-01 20:55:12.576778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '66b02583fc42'
down_revision: Union[str, None] = '9fd7e97a72af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('sensor_position_constraint', 'stationsensorassignments', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('sensor_position_constraint', 'stationsensorassignments', ['station_id', 'sensor_position'])
    # ### end Alembic commands ###
