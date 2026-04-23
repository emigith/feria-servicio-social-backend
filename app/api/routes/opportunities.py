from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student
from app.core.db import get_db
from app.schemas.enrollment import EnrollmentResponse
from app.schemas.opportunity import OpportunityDetailResponse, OpportunityResponse
from app.services.enrollment_service import enroll_student_in_opportunity
from app.services.opportunity_service import (
    get_opportunities_by_period_id,
    get_opportunities_for_active_period,
    get_opportunity_by_id,
)

router = APIRouter(prefix="/opportunities")


@router.get("", response_model=list[OpportunityResponse])
def list_opportunities(
    period: str = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_student),
):
    if period == "active":
        return get_opportunities_for_active_period(db)

    try:
        period_uuid = UUID(period)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="period must be 'active' or a valid UUID",
        )

    return get_opportunities_by_period_id(db, period_uuid)


@router.get("/{opportunity_id}", response_model=OpportunityDetailResponse)
def get_opportunity_endpoint(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),  # solo requiere login, no check-in
):
    return get_opportunity_by_id(opportunity_id, db)


from app.services.email_service import send_enrollment_confirmation

@router.post("/{opportunity_id}/enroll", response_model=EnrollmentResponse, status_code=201)
def enroll_in_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    enrollment = enroll_student_in_opportunity(
        opportunity_id=opportunity_id,
        student_id=current_student.id,
        db=db,
    )
    
    opportunity = get_opportunity_by_id(opportunity_id, db)
    
    send_enrollment_confirmation(
        to_email=current_student.email,
        student_name=current_student.nombre,
        opportunity_title=opportunity.title,
        company_name=opportunity.company
    )
    
    return enrollment