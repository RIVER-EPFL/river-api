"""Add sensor relationship to parameter

Revision ID: d057ad1a2a31
Revises: 09651fa5f642
Create Date: 2024-04-18 11:15:10.689261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd057ad1a2a31'
down_revision: Union[str, None] = '09651fa5f642'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensor', sa.Column('parameter_id', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensor', 'parameter_id')
    # ### end Alembic commands ###
