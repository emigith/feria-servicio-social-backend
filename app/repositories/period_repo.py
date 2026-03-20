from uuid import UUID

from sqlalchemy.orm import Session

from app.models.period import Period


class PeriodRepo:
    def get_active(self, db: Session) -> Period | None:
        return db.query(Period).filter(Period.is_active == True).first()

    def get_by_name(self, db: Session, name: str) -> Period | None:
        return db.query(Period).filter(Period.name == name).first()

    def get_by_id(self, db: Session, period_id: UUID) -> Period | None:
        return db.query(Period).filter(Period.id == period_id).first()

    def create(
        self,
        db: Session,
        name: str,
        starts_at,
        ends_at,
        is_active: bool,
    ) -> Period:
        period = Period(
            name=name,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active,
        )
        db.add(period)
        db.commit()
        db.refresh(period)
        return period