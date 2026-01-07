"""fix room_members cascade delete

Revision ID: 10ccb23fa944
Revises: eb5a889cf092
Create Date: 2026-01-07 20:23:27.308822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10ccb23fa944'
down_revision: Union[str, Sequence[str], None] = 'eb5a889cf092'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
