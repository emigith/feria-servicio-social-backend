from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.opportunity_repo import OpportunityRepo


repo = OpportunityRepo()


def get_partner_opportunities(partner_user_id: UUID, db: Session):
    return repo.get_by_partner_user(db, partner_user_id)


def get_partner_general_dashboard(partner_user_id: UUID, db: Session):
    opportunities = repo.get_by_partner_user(db, partner_user_id)

    total_capacity = sum(o.capacity for o in opportunities)
    total_enrolled = sum(o.enrolled_count for o in opportunities)
    overall_rate = round((total_enrolled / total_capacity) * 100, 2) if total_capacity > 0 else 0.0

    return {
        "total_opportunities": len(opportunities),
        "total_enrolled": total_enrolled,
        "total_capacity": total_capacity,
        "overall_enrollment_rate": overall_rate,
        "opportunities": [
            {
                "id": o.id,
                "title": o.title,
                "company": o.company,
                "capacity": o.capacity,
                "enrolled_count": o.enrolled_count,
                "available_slots": o.available_slots,
                "is_full": o.is_full,
                "enrollment_rate": round((o.enrolled_count / o.capacity) * 100, 2) if o.capacity > 0 else 0.0,
            }
            for o in opportunities
        ],
    }


def get_partner_opportunity_enrollments(
    partner_user_id: UUID,
    opportunity_id: UUID,
    db: Session,
):
    opportunity = repo.get_by_id_for_partner(db, opportunity_id, partner_user_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    rows = repo.get_enrollments_for_partner_opportunity(db, opportunity_id, partner_user_id)

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
                "status": enrollment.status,
                "created_at": enrollment.created_at,
            }
            for enrollment, student in rows
        ],
    }


def get_partner_opportunity_dashboard(
    partner_user_id: UUID,
    opportunity_id: UUID,
    db: Session,
):
    opportunity = repo.get_by_id_for_partner(db, opportunity_id, partner_user_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OPPORTUNITY_NOT_FOUND",
        )

    enrolled_count = opportunity.enrolled_count
    available_slots = opportunity.available_slots
    enrollment_rate = 0.0

    if opportunity.capacity > 0:
        enrollment_rate = round((enrolled_count / opportunity.capacity) * 100, 2)

    return {
        "opportunity_id": opportunity.id,
        "title": opportunity.title,
        "company": opportunity.company,
        "capacity": opportunity.capacity,
        "enrolled_count": enrolled_count,
        "available_slots": available_slots,
        "is_full": opportunity.is_full,
        "enrollment_rate": enrollment_rate,
    }