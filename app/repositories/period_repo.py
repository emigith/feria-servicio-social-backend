from uuid import UUID

from sqlalchemy.orm import Session

from app.models.period import Period


class PeriodRepo:
    def get_all(self, db: Session) -> list[Period]:
        return db.query(Period).order_by(Period.starts_at).all()

    def get_active(self, db: Session) -> Period | None:
        # Ordenar por starts_at DESC para devolver el período activo más reciente
        # en caso de que haya más de uno marcado como activo
        return (
            db.query(Period)
            .filter(Period.is_active == True)
            .order_by(Period.starts_at.desc())
            .first()
        )

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