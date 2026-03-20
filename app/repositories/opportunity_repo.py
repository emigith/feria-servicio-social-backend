from uuid import UUID

from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity


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
    ) -> Opportunity:
        opportunity = Opportunity(
            period_id=period_id,
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
    ) -> Opportunity:
        """Actualiza solo los campos que se manden (PATCH parcial)."""
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

        db.commit()
        db.refresh(opportunity)
        return opportunity