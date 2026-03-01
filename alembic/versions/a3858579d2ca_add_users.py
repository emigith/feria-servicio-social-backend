"""add users

Revision ID: a3858579d2ca
Revises: a77db637bd80
Create Date: 2026-02-28 19:46:07.850482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a3858579d2ca"
down_revision: Union[str, Sequence[str], None] = "a77db637bd80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
