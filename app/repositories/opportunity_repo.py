from uuid import UUID

from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity


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