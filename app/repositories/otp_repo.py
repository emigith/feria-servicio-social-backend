from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.otp_code import OtpCode


class OtpRepo:
    def get_latest_active_by_student(self, db: Session, student_id: UUID) -> OtpCode | None:
        return (
            db.query(OtpCode)
            .filter(
                OtpCode.student_id == student_id,
                OtpCode.used_at.is_(None),
            )
            .order_by(OtpCode.created_at.desc())
            .first()
        )

    def create(
        self,
        db: Session,
        student_id: UUID,
        code_hash: str,
        expires_at: datetime,
    ) -> OtpCode:
        otp = OtpCode(
            student_id=student_id,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)
        return otp

    def mark_used(self, db: Session, otp: OtpCode) -> OtpCode:
        otp.used_at = datetime.now(timezone.utc)
        db.add(otp)
        db.commit()
        db.refresh(otp)
        return otp