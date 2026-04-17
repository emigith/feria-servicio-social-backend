from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.enrollment_repo import EnrollmentRepo
from app.repositories.opportunity_repo import OpportunityRepo


def enroll_student_in_opportunity(opportunity_id: UUID, student_id: UUID, db: Session):
    opportunity_repo = OpportunityRepo()
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

    # Un alumno solo puede inscribirse a un proyecto por período
    existing_enrollment = enrollment_repo.get_by_student_and_period(
        db,
        student_id=student_id,
        period_id=opportunity.period_id,
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
            period_id=opportunity.period_id,
            status="ENROLLED",
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_ENROLLED_THIS_PERIOD",
        )