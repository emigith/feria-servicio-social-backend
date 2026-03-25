"""add socioformador role and partner_user_id to opportunities

Revision ID: ce921731eafc
Revises: f79c88cd9244
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce921731eafc'
down_revision: Union[str, Sequence[str], None] = 'f79c88cd9244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Agregar nuevo valor al enum user_role en Postgres
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'socioformador'")

    # 2) Agregar columna partner_user_id a opportunities
    op.add_column(
        'opportunities',
        sa.Column('partner_user_id', sa.UUID(), nullable=True)
    )

    # 3) Crear foreign key hacia users.id
    op.create_foreign_key(
        'fk_opportunities_partner_user_id_users',
        'opportunities',
        'users',
        ['partner_user_id'],
        ['id'],
        ondelete='SET NULL',
    )

    # 4) Crear índice para filtros por socioformador
    op.create_index(
        'idx_opportunities_partner_user_id',
        'opportunities',
        ['partner_user_id'],
        unique=False,
    )


def downgrade() -> None:
    # 1) Quitar índice
    op.drop_index('idx_opportunities_partner_user_id', table_name='opportunities')

    # 2) Quitar foreign key
    op.drop_constraint(
        'fk_opportunities_partner_user_id_users',
        'opportunities',
        type_='foreignkey',
    )

    # 3) Quitar columna
    op.drop_column('opportunities', 'partner_user_id')

    # 4) NO intentamos remover el valor del enum porque en Postgres eso es delicado
    # y normalmente no se hace en downgrade simple.