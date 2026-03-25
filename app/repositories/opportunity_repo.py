from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.opportunity import Opportunity
from app.models.student import Student


class OpportunityRepo:

    # --- Endpoints existentes de Emilio (no tocar) ---

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

    # --- Métodos nuevos para ADMIN ---

    def get_all(self, db: Session) -> list[Opportunity]:
        """Lista todas las oportunidades (activas e inactivas) para el panel admin."""
        return db.query(Opportunity).order_by(Opportunity.created_at.desc()).all()

    def create(
        self,
        db: Session,
        period_id: UUID,
        title: str,
        company: str,
        capacity: int,
        description: str | None = None,
        location: str | None = None,
        is_active: bool = True,
        partner_user_id: UUID | None = None,
    ) -> Opportunity:
        opportunity = Opportunity(
            period_id=period_id,
            partner_user_id=partner_user_id,
            title=title,
            company=company,
            capacity=capacity,
            description=description,
            location=location,
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
        title: str | None = None,
        company: str | None = None,
        capacity: int | None = None,
        description: str | None = None,
        location: str | None = None,
        is_active: bool | None = None,
        partner_user_id: UUID | None = None,
    ) -> Opportunity:
        if title is not None:
            opportunity.title = title
        if company is not None:
            opportunity.company = company
        if capacity is not None:
            opportunity.capacity = capacity
        if description is not None:
            opportunity.description = description
        if location is not None:
            opportunity.location = location
        if is_active is not None:
            opportunity.is_active = is_active
        if partner_user_id is not None:
            opportunity.partner_user_id = partner_user_id

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

    def get_enrollments_for_partner_opportunity(
        self,
        db: Session,
        opportunity_id: UUID,
        partner_user_id: UUID,
    ):
        return (
            db.query(Enrollment, Student)
            .join(Student, Enrollment.student_id == Student.id)
            .join(Opportunity, Enrollment.opportunity_id == Opportunity.id)
            .filter(
                Enrollment.opportunity_id == opportunity_id,
                Opportunity.partner_user_id == partner_user_id,
            )
            .order_by(Enrollment.created_at.asc())
            .all()
        )

    def get_by_partner_user(self, db: Session, partner_user_id: UUID) -> list[Opportunity]:
        return (
            db.query(Opportunity)
            .filter(Opportunity.partner_user_id == partner_user_id)
            .order_by(Opportunity.created_at.desc())
            .all()
        )

    def get_by_id_for_partner(
        self,
        db: Session,
        opportunity_id: UUID,
        partner_user_id: UUID,
    ) -> Opportunity | None:
        return (
            db.query(Opportunity)
            .filter(
                Opportunity.id == opportunity_id,
                Opportunity.partner_user_id == partner_user_id,
            )
            .first()
        )