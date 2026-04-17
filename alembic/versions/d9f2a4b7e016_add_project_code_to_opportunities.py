"""add project_code to opportunities

Revision ID: d9f2a4b7e016
Revises: c7d3e8a1f042
Create Date: 2026-04-17 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd9f2a4b7e016'
down_revision = 'c7d3e8a1f042'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('opportunities', sa.Column('project_code', sa.String(30), nullable=True))
    op.create_index('ix_opportunities_project_code', 'opportunities', ['project_code'])


def downgrade() -> None:
    op.drop_index('ix_opportunities_project_code', table_name='opportunities')
    op.drop_column('opportunities', 'project_code')
