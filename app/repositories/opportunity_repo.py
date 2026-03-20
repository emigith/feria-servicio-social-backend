from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.opportunity import Opportunity
from app.models.student import Student


class OpportunityRepo:
    def get_active_by_period(self, db: Session, period_id: UUID) -> list[Opportunity]:
        return (
            db.query(Opportunity)
            .filter(
                Opportunity.period_id == period_id,
                Opportunity.is_active == True,
            )
            .all()
        )

    def get_by_id(self, db: Session, opportunity_id: UUID) -> Opportunity | None:
        return (
            db.query(Opportunity)
            .filter(Opportunity.id == opportunity_id)
            .first()
        )

    def create(
        self,
        db: Session,
        period_id: UUID,
        title: str,
        description: str | None,
        company: str,
        location: str | None,
        capacity: int,
        is_active: bool = True,
    ) -> Opportunity:
        opportunity = Opportunity(
            period_id=period_id,
            title=title,
            description=description,
            company=company,
            location=location,
            capacity=capacity,
            is_active=is_active,
        )
        db.add(opportunity)
        db.commit()
        db.refresh(opportunity)
        return opportunity

    def update(
        self,
        db: Session,
        opportunity: Opportunity,
        period_id: UUID,
        title: str,
        description: str | None,
        company: str,
        location: str | None,
        capacity: int,
        is_active: bool,
    ) -> Opportunity:
        opportunity.period_id = period_id
        opportunity.title = title
        opportunity.description = description
        opportunity.company = company
        opportunity.location = location
        opportunity.capacity = capacity
        opportunity.is_active = is_active

        db.add(opportunity)
        db.commit()
        db.refresh(opportunity)
        return opportunity

    def set_active_status(
        self,
        db: Session,
        opportunity: Opportunity,
        is_active: bool,
    ) -> Opportunity:
        opportunity.is_active = is_active
        db.add(opportunity)
        db.commit()
        db.refresh(opportunity)
        return opportunity

    def get_enrollments(self, db: Session, opportunity_id: UUID):
        return (
            db.query(Enrollment, Student)
            .join(Student, Enrollment.student_id == Student.id)
            .filter(Enrollment.opportunity_id == opportunity_id)
            .order_by(Enrollment.created_at.asc())
            .all()
        )