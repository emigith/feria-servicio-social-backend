from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.repositories.checkin_repo import CheckinRepo


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