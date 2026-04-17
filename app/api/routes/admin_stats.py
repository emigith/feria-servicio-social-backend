from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.db import get_db
from app.services.admin_stats_service import get_admin_stats

router = APIRouter(prefix="/admin/stats", tags=["admin-stats"])


@router.get("")
def admin_stats(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Devuelve todos los KPIs del dashboard admin con datos reales."""
    return get_admin_stats(db)
