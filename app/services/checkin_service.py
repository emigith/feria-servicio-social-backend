from datetime import datetime, timedelta, timezone
from secrets import randbelow
from uuid import UUID

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.repositories.checkin_repo import CheckinRepo
from app.repositories.otp_repo import OtpRepo
from app.repositories.student_repo import StudentRepo
from app.services.email_service import send_otp_email


OTP_EXPIRATION_MINUTES = 10


def _generate_otp_code() -> str:
    return f"{randbelow(1000000):06d}"


def _hash_otp_code(raw_code: str) -> str:
    return bcrypt.hashpw(raw_code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_otp_code(raw_code: str, code_hash: str) -> bool:
    return bcrypt.checkpw(raw_code.encode("utf-8"), code_hash.encode("utf-8"))


def request_otp_for_current_student(student_id: UUID, db: Session):
    otp_repo = OtpRepo()
    checkin_repo = CheckinRepo()
    student_repo = StudentRepo()

    student = student_repo.get_by_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="STUDENT_NOT_FOUND",
        )

    existing_checkin = checkin_repo.get_by_student(db, student_id)
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_CHECKED_IN",
        )

    raw_code = _generate_otp_code()
    code_hash = _hash_otp_code(raw_code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    otp_repo.create(
        db=db,
        student_id=student_id,
        code_hash=code_hash,
        expires_at=expires_at,
    )

    send_otp_email(
        to_email=student.email,
        otp_code=raw_code,
        student_name=getattr(student, "nombre", None),
    )

    return {
        "student_id": student_id,
        "expires_at": expires_at,
        "message": "OTP_SENT",
    }


def checkin_current_student(
    student_id: UUID,
    otp_code: str,
    db: Session,
    method: str | None = None,
    device: str | None = None,
):
    otp_repo = OtpRepo()
    checkin_repo = CheckinRepo()

    existing_checkin = checkin_repo.get_by_student(db, student_id)
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_CHECKED_IN",
        )

    otp = otp_repo.get_latest_active_by_student(db, student_id)
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP_NOT_FOUND",
        )

    if otp.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="OTP_ALREADY_USED",
        )

    now = datetime.now(timezone.utc)
    expires_at = otp.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP_EXPIRED",
        )

    if not _verify_otp_code(otp_code, otp.code_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP_INVALID",
        )

    try:
        otp_repo.mark_used(db, otp)
        checkin = checkin_repo.create(
            db=db,
            student_id=student_id,
            method=method,
            device=device,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_CHECKED_IN",
        )

    access_token = create_access_token(
        subject=str(student_id),
        role="student",
        token_type="student",
    )

    return {
        "student_id": student_id,
        "checked_in_at": checkin.checked_in_at,
        "method": checkin.method,
        "device": checkin.device,
        "message": "CHECKIN_SUCCESSFUL",
        "access_token": access_token,
        "token_type": "bearer",
    }

def checkin_student_by_qr(
    student_id: UUID,
    db: Session,
    method: str | None = None,
    device: str | None = None,
):
    checkin_repo = CheckinRepo()

    existing_checkin = checkin_repo.get_by_student(db, student_id)
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_CHECKED_IN",
        )

    try:
        checkin = checkin_repo.create(
            db=db,
            student_id=student_id,
            method=method,
            device=device,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ALREADY_CHECKED_IN",
        )

    access_token = create_access_token(
        subject=str(student_id),
        role="student",
        token_type="student",
    )

    return {
        "student_id": student_id,
        "checked_in_at": checkin.checked_in_at,
        "method": checkin.method,
        "device": checkin.device,
        "message": "CHECKIN_SUCCESSFUL",
        "access_token": access_token,
        "token_type": "bearer",
    }