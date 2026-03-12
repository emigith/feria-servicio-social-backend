from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.opportunity_repo import OpportunityRepo
from app.repositories.period_repo import PeriodRepo


def get_opportunities_for_active_period(db: Session):
    period_repo = PeriodRepo()
    opportunity_repo = OpportunityRepo()

    active_period = period_repo.get_active(db)
    if not active_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active period found",
        )

    return opportunity_repo.get_active_by_period(db, active_period.id)


def get_opportunity_by_id(opportunity_id: UUID, db: Session):
    repo = OpportunityRepo()
    opportunity = repo.get_by_id(db, opportunity_id)

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    return opportunity