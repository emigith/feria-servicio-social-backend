from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.enrollment_repo import EnrollmentRepo
from app.repositories.opportunity_repo import OpportunityRepo
from app.repositories.period_repo import PeriodRepo


def enroll_student_in_opportunity(opportunity_id: UUID, student_id: UUID, db: Session):
    opportunity_repo = OpportunityRepo()
    period_repo = PeriodRepo()
    enrollment_repo = EnrollmentRepo()

    opportunity = opportunity_repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    if not opportunity.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OPPORTUNITY_INACTIVE",
        )

    active_period = period_repo.get_active(db)
    if not active_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_ACTIVE_PERIOD",
        )

    if opportunity.period_id != active_period.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OPPORTUNITY_NOT_IN_ACTIVE_PERIOD",
        )

    existing_enrollment = enrollment_repo.get_by_student_and_period(
        db,
        student_id=student_id,
        period_id=active_period.id,
    )
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_ENROLLED_THIS_PERIOD",
        )

    enrolled_count = enrollment_repo.count_by_opportunity(db, opportunity.id)
    if enrolled_count >= opportunity.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="OPPORTUNITY_FULL",
        )

    try:
        return enrollment_repo.create(
            db=db,
            student_id=student_id,
            opportunity_id=opportunity.id,
            period_id=active_period.id,
            status="ENROLLED",
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_ENROLLED_THIS_PERIOD",
        )