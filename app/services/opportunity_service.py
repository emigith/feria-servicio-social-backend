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


def create_opportunity(
    db: Session,
    period_id: UUID,
    title: str,
    description: str | None,
    company: str,
    location: str | None,
    capacity: int,
    is_active: bool = True,
):
    period_repo = PeriodRepo()
    opportunity_repo = OpportunityRepo()

    period = period_repo.get_by_id(db, period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PERIOD_NOT_FOUND",
        )

    if capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_CAPACITY",
        )

    return opportunity_repo.create(
        db=db,
        period_id=period_id,
        title=title,
        description=description,
        company=company,
        location=location,
        capacity=capacity,
        is_active=is_active,
    )


def update_opportunity(
    opportunity_id: UUID,
    db: Session,
    period_id: UUID,
    title: str,
    description: str | None,
    company: str,
    location: str | None,
    capacity: int,
    is_active: bool,
):
    period_repo = PeriodRepo()
    opportunity_repo = OpportunityRepo()

    opportunity = opportunity_repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    period = period_repo.get_by_id(db, period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PERIOD_NOT_FOUND",
        )

    if capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_CAPACITY",
        )

    enrolled_count = opportunity.enrolled_count
    if capacity < enrolled_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPACITY_BELOW_ENROLLED_COUNT",
        )

    return opportunity_repo.update(
        db=db,
        opportunity=opportunity,
        period_id=period_id,
        title=title,
        description=description,
        company=company,
        location=location,
        capacity=capacity,
        is_active=is_active,
    )


def activate_opportunity(opportunity_id: UUID, db: Session):
    opportunity_repo = OpportunityRepo()

    opportunity = opportunity_repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    return opportunity_repo.set_active_status(db, opportunity, True)


def deactivate_opportunity(opportunity_id: UUID, db: Session):
    opportunity_repo = OpportunityRepo()

    opportunity = opportunity_repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    return opportunity_repo.set_active_status(db, opportunity, False)


def get_opportunity_enrollments(opportunity_id: UUID, db: Session):
    opportunity_repo = OpportunityRepo()

    opportunity = opportunity_repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    rows = opportunity_repo.get_enrollments(db, opportunity_id)

    return {
        "opportunity_id": opportunity.id,
        "title": opportunity.title,
        "company": opportunity.company,
        "total_enrollments": len(rows),
        "enrollments": [
            {
                "enrollment_id": enrollment.id,
                "student_id": student.id,
                "matricula": student.matricula,
                "nombre": student.nombre,
                "apellido": student.apellido,
                "email": student.email,
                "status": enrollment.status,
                "enrolled_at": enrollment.created_at,
            }
            for enrollment, student in rows
        ],
    }