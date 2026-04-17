"""add credit_hours to opportunities

Revision ID: c7d3e8a1f042
Revises: b4e2f1c9d305
Create Date: 2026-04-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c7d3e8a1f042'
down_revision = 'b4e2f1c9d305'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('opportunities', sa.Column('credit_hours', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('opportunities', 'credit_hours')
