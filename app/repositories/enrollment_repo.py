from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment


class EnrollmentRepo:
    def get_by_student_and_period(self, db: Session, student_id: UUID, period_id: UUID) -> Enrollment | None:
        return (
            db.query(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.period_id == period_id,
            )
            .first()
        )

    def count_by_opportunity(self, db: Session, opportunity_id: UUID) -> int:
        return (
            db.query(Enrollment)
            .filter(
                Enrollment.opportunity_id == opportunity_id,
                Enrollment.status.in_(["ENROLLED", "CHECKED_IN"]),
            )
            .count()
        )

    def create(
        self,
        db: Session,
        student_id: UUID,
        opportunity_id: UUID,
        period_id: UUID,
        status: str = "ENROLLED",
    ) -> Enrollment:
        enrollment = Enrollment(
            student_id=student_id,
            opportunity_id=opportunity_id,
            period_id=period_id,
            status=status,
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment
    
    def update_status(self, db: Session, enrollment: Enrollment, status: str) -> Enrollment:
        enrollment.status = status
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment
    def get_by_opportunity(self, db: Session, opportunity_id: UUID) -> list[Enrollment]:
        """Lista todos los inscritos en una oportunidad."""
        return (
            db.query(Enrollment)
            .filter(Enrollment.opportunity_id == opportunity_id)
            .all()
        )

    def get_by_id(self, db: Session, enrollment_id: UUID) -> Enrollment | None:
        return db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    def delete(self, db: Session, enrollment: Enrollment) -> None:
        db.delete(enrollment)
        db.commit()

