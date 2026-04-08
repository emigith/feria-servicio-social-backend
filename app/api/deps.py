from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_token
from app.repositories.checkin_repo import CheckinRepo
from app.repositories.student_repo import StudentRepo
from app.repositories.user_repo import UserRepo

bearer_scheme = HTTPBearer()


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    try:
        return decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_student(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
):
    if payload.get("type") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student token required",
        )

    student_id = payload.get("sub")
    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    repo = StudentRepo()
    student = repo.get_by_id(db, UUID(student_id))
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


def get_checked_in_student(
    db: Session = Depends(get_db),
    student=Depends(get_current_student),
):
    """Igual que get_current_student pero además exige que el alumno haya hecho check-in."""
    checkin_repo = CheckinRepo()
    checkin = checkin_repo.get_by_student(db, student.id)
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CHECKIN_REQUIRED",
        )
    return student


def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
):
    if payload.get("type") != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User token required",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    repo = UserRepo(db)
    user = repo.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def require_roles(allowed_roles: list[str]):
    def checker(current_user=Depends(get_current_user)):
        print("ROLE RAW:", current_user.role)
        print("ROLE VALUE:", getattr(current_user.role, "value", None))
        print("ALLOWED:", allowed_roles)

        current_role = current_user.role.value.upper()
        normalized_allowed_roles = [role.upper() for role in allowed_roles]

        print("NORMALIZED CURRENT:", current_role)
        print("NORMALIZED ALLOWED:", normalized_allowed_roles)

        if current_role not in normalized_allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker