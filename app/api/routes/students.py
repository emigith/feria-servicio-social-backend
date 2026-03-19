from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student
from app.core.db import get_db
from app.schemas.checkin import CheckinRequest, CheckinResponse, OtpRequestResponse
from app.services.checkin_service import (
    checkin_current_student,
    request_otp_for_current_student,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/me/otp/request", response_model=OtpRequestResponse, status_code=status.HTTP_201_CREATED)
def request_my_otp(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return request_otp_for_current_student(
        student_id=current_student.id,
        db=db,
    )


@router.post("/me/checkin", response_model=CheckinResponse, status_code=status.HTTP_200_OK)
def checkin_me(
    payload: CheckinRequest,
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