"""add indexes for opportunities and enrollments

Revision ID: 6bcd42a41138
Revises: f277775d6db1
Create Date: 2026-03-11 16:51:36.053665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bcd42a41138'
down_revision: Union[str, Sequence[str], None] = 'f277775d6db1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_opportunities_period_id', 'opportunities', ['period_id'], unique=False)
    op.create_index('idx_opportunities_period_active', 'opportunities', ['period_id', 'is_active'], unique=False)
    op.create_index('idx_enrollments_student_id', 'enrollments', ['student_id'], unique=False)
    op.create_index('idx_enrollments_opportunity_id', 'enrollments', ['opportunity_id'], unique=False)
    op.create_index('idx_enrollments_period_id', 'enrollments', ['period_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_enrollments_period_id', table_name='enrollments')
    op.drop_index('idx_enrollments_opportunity_id', table_name='enrollments')
    op.drop_index('idx_enrollments_student_id', table_name='enrollments')
    op.drop_index('idx_opportunities_period_active', table_name='opportunities')
    op.drop_index('idx_opportunities_period_id', table_name='opportunities')
