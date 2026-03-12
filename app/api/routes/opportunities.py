from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student
from app.core.db import get_db
from app.schemas.opportunity import OpportunityDetailResponse, OpportunityResponse
from app.services.opportunity_service import (
    get_opportunities_for_active_period,
    get_opportunity_by_id,
)

router = APIRouter(prefix="/opportunities")


@router.get("", response_model=list[OpportunityResponse])
def list_opportunities(
    period: str = Query(...),
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    if period != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only period=active is supported",
        )

    return get_opportunities_for_active_period(db)


@router.get("/{opportunity_id}", response_model=OpportunityDetailResponse)
def get_opportunity_endpoint(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return get_opportunity_by_id(opportunity_id, db)