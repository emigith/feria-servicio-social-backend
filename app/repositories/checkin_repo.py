from uuid import UUID

from sqlalchemy.orm import Session

from app.models.checkin import Checkin


class CheckinRepo:
    def get_by_student(self, db: Session, student_id: UUID) -> Checkin | None:
        return (
            db.query(Checkin)
            .filter(Checkin.student_id == student_id)
            .first()
        )

    def create(
        self,
        db: Session,
        student_id: UUID,
        method: str | None = None,
        device: str | None = None,
    ) -> Checkin:
        checkin = Checkin(
            student_id=student_id,
            method=method,
            device=device,
        )
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        return checkin