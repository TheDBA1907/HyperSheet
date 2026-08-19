"""add market history tables

Revision ID: c196c33000d1
Revises: 30d3fbd17338
Create Date: 2026-08-17 21:12:47.821439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c196c33000d1'
down_revision: Union[str, Sequence[str], None] = '30d3fbd17338'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
