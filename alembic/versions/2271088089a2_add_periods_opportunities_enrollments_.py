"""add periods opportunities enrollments otp_codes

Revision ID: 2271088089a2
Revises: 20139ef85cc9
Create Date: 2026-03-04 18:29:15.399911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2271088089a2'
down_revision: Union[str, Sequence[str], None] = '20139ef85cc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
