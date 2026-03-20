from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student, require_roles
from app.core.db import get_db
from app.repositories.student_repo import StudentRepo
from app.schemas.checkin import CheckinPublicRequest, CheckinResponse, OtpRequestResponse
from app.services.checkin_service import (
    checkin_current_student,
    request_otp_for_current_student,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.post(
    "/becario/{matricula}/send-otp",
    response_model=OtpRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Becario envía OTP al estudiante",
)
def send_otp_to_student(
    matricula: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "intern"])),
):
    repo = StudentRepo()
    student = repo.get_by_matricula(db, matricula)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="STUDENT_NOT_FOUND",
        )

    return request_otp_for_current_student(
        student_id=student.id,
        db=db,
    )


@router.post(
    "/checkin",
    response_model=CheckinResponse,
    status_code=status.HTTP_200_OK,
    summary="Check-in público con matrícula + OTP",
)
def public_checkin(
    payload: CheckinPublicRequest,
    db: Session = Depends(get_db),
):
    repo = StudentRepo()
    student = repo.get_by_matricula(db, payload.matricula)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="STUDENT_NOT_FOUND",
        )

    return checkin_current_student(
        student_id=student.id,
        otp_code=payload.otp_code,
        method=payload.method,
        device=payload.device,
        db=db,
    )


@router.post(
    "/me/otp/request",
    response_model=OtpRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Interno] Alumno autenticado pide su OTP",
    include_in_schema=False,
)
def request_my_otp(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return request_otp_for_current_student(
        student_id=current_student.id,
        db=db,
    )


@router.post(
    "/me/checkin",
    response_model=CheckinResponse,
    status_code=status.HTTP_200_OK,
    summary="[Interno] Check-in con JWT de alumno",
    include_in_schema=False,
)
def checkin_me(
    payload: CheckinPublicRequest,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return checkin_current_student(
        student_id=current_student.id,
        otp_code=payload.otp_code,
        method=payload.method,
        device=payload.device,
        db=db,
    )