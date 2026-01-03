"""initial schema

Revision ID: 3d08ec8e957f
Revises: 
Create Date: 2026-01-03 15:36:12.148033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3d08ec8e957f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_guest', sa.Boolean(), nullable=False, server_default='false'))

def downgrade() -> None:
    op.drop_column('users', 'is_guest')