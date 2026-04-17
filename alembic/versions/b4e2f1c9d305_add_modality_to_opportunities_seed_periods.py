"""add_modality_to_opportunities_seed_periods

Revision ID: b4e2f1c9d305
Revises: 083bf596be01
Create Date: 2026-04-17 10:00:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


revision: str = 'b4e2f1c9d305'
down_revision: Union[str, Sequence[str], None] = '083bf596be01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Períodos fijos de la feria
PERIODS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Enero-Junio",
        "starts_at": "2026-01-05 00:00:00+00",
        "ends_at":   "2026-06-30 23:59:59+00",
        "is_active": False,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Verano",
        "starts_at": "2026-06-01 00:00:00+00",
        "ends_at":   "2026-07-31 23:59:59+00",
        "is_active": False,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Agosto-Diciembre",
        "starts_at": "2026-08-01 00:00:00+00",
        "ends_at":   "2026-12-20 23:59:59+00",
        "is_active": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Invierno",
        "starts_at": "2026-12-01 00:00:00+00",
        "ends_at":   "2027-01-15 23:59:59+00",
        "is_active": False,
    },
]


def upgrade() -> None:
    # ── 1. Agregar columna modality a opportunities ────────────────────────
    op.add_column(
        "opportunities",
        sa.Column("modality", sa.String(20), nullable=False, server_default="Presencial"),
    )

    # ── 2. Insertar los 4 períodos (ignorar si ya existen por nombre) ──────
    conn = op.get_bind()
    for p in PERIODS:
        exists = conn.execute(
            sa.text("SELECT 1 FROM periods WHERE name = :name"),
            {"name": p["name"]},
        ).fetchone()
        if not exists:
            conn.execute(
                sa.text(
                    "INSERT INTO periods (id, name, starts_at, ends_at, is_active) "
                    "VALUES (:id, :name, :starts_at, :ends_at, :is_active)"
                ),
                {
                    "id": p["id"],
                    "name": p["name"],
                    "starts_at": p["starts_at"],
                    "ends_at": p["ends_at"],
                    "is_active": p["is_active"],
                },
            )


def downgrade() -> None:
    op.drop_column("opportunities", "modality")
    # No eliminamos los períodos en downgrade para no perder datos reales
