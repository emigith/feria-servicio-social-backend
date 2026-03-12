from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.db import get_db
from app.schemas.period import PeriodCreateRequest, PeriodResponse
from app.services.period_service import create_period, get_active_period

router = APIRouter(prefix="/periods")


@router.get("/active", response_model=PeriodResponse)
def get_active_period_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN", "INTERN"])),
):
    return get_active_period(db)


@router.post("", response_model=PeriodResponse, status_code=201)
def create_period_endpoint(
    payload: PeriodCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN", "INTERN"])),
):
    return create_period(
        name=payload.name,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        is_active=payload.is_active,
        db=db,
    )