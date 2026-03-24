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
# Añade esta línea al principio de tu archivo de rutas
from app.schemas.student_views import StudentUpdateSchema



from app.schemas.student_views import (
    StudentActiveEnrollmentResponse,
    StudentCheckinStatusResponse,
    StudentEnrollmentHistoryResponse,
    StudentMeResponse,
)
from app.services.student_view_service import (
    get_current_student_active_enrollment,
    get_current_student_checkin_status,
    get_current_student_enrollment_history,
    get_current_student_profile,
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


@router.get(
    "/me",
    response_model=StudentMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Perfil del estudiante autenticado",
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return get_current_student_profile(
        student_id=current_student.id,
        db=db,
    )


@router.get(
    "/me/checkin-status",
    response_model=StudentCheckinStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Estado de check-in del estudiante autenticado",
)
def get_my_checkin_status(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return get_current_student_checkin_status(
        student_id=current_student.id,
        db=db,
    )


@router.get(
    "/me/enrollment",
    response_model=StudentActiveEnrollmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Inscripción activa del estudiante autenticado",
)
def get_my_active_enrollment(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return get_current_student_active_enrollment(
        student_id=current_student.id,
        db=db,
    )


@router.get(
    "/me/history",
    response_model=StudentEnrollmentHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Historial de inscripciones del estudiante autenticado",
)
def get_my_enrollment_history(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    return get_current_student_enrollment_history(
        student_id=current_student.id,
        db=db,
    )

# app/api/routes/students.py (o donde tengas las rutas de 'me')

@router.patch("/me", status_code=status.HTTP_200_OK)
def update_profile(
    payload: StudentUpdateSchema, # Crea un schema con nombre, apellido, correo (opcionales)
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student) # El token que guardamos arriba
):
    repo = StudentRepo()
    updated_student = repo.update(db, student_id=current_student.id, data=payload.dict(exclude_unset=True))
    return updated_student