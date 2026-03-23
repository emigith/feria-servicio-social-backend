from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.student_queries import (
    get_active_enrollment,
    get_checkin_status,
    get_enrollment_history,
    get_student_profile,
)


def get_current_student_profile(student_id, db: Session):
    student = get_student_profile(db, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="STUDENT_NOT_FOUND",
        )

    return student


def get_current_student_checkin_status(student_id, db: Session):
    checkin = get_checkin_status(db, student_id)

    if not checkin:
        return {
            "has_checkin": False,
            "checked_in_at": None,
            "method": None,
            "device": None,
        }

    return {
        "has_checkin": True,
        "checked_in_at": checkin.checked_in_at,
        "method": checkin.method,
        "device": checkin.device,
    }


def get_current_student_active_enrollment(student_id, db: Session):
    enrollment = get_active_enrollment(db, student_id)

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_ACTIVE_ENROLLMENT",
        )

    return {
        "enrollment_id": enrollment.id,
        "opportunity_id": enrollment.opportunity.id,
        "period_id": enrollment.period.id,
        "period_name": enrollment.period.name,
        "title": enrollment.opportunity.title,
        "company": enrollment.opportunity.company,
        "location": enrollment.opportunity.location,
        "status": enrollment.status,
        "enrolled_at": enrollment.created_at,
    }


def get_current_student_enrollment_history(student_id, db: Session):
    rows = get_enrollment_history(db, student_id)

    items = []
    for enrollment in rows:
        items.append(
            {
                "enrollment_id": enrollment.id,
                "opportunity_id": enrollment.opportunity.id,
                "period_id": enrollment.period.id,
                "period_name": enrollment.period.name,
                "title": enrollment.opportunity.title,
                "company": enrollment.opportunity.company,
                "location": enrollment.opportunity.location,
                "status": enrollment.status,
                "enrolled_at": enrollment.created_at,
            }
        )

    return {
        "total": len(items),
        "items": items,
    }