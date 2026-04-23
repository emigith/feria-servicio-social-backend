"""otp_checkins_migrate_to_student_id

Revision ID: f79c88cd9244
Revises: ac97ed44f2d0
Create Date: 2026-03-19 08:53:48.408309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f79c88cd9244'
down_revision: Union[str, Sequence[str], None] = 'ac97ed44f2d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

