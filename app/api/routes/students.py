from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student, require_roles
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from app.core.config import settings
from app.core.db import get_db
from app.repositories.student_repo import StudentRepo
from app.schemas.checkin import CheckinPublicRequest, CheckinResponse, OtpRequestResponse, QRCheckinRequest
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


@router.post(
    "/verify-info",
    status_code=status.HTTP_200_OK,
    summary="[Interno] Alumno verifica info y pide QR",
)
def verify_student_info(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    from app.services.qr_service import generate_qr_base64_for_checkin
    from app.services.email_service import send_qr_code_email

    qr_base64 = generate_qr_base64_for_checkin(current_student.id, current_student.matricula)
    
    send_qr_code_email(
        to_email=current_student.email,
        student_name=current_student.nombre,
        qr_base64=qr_base64
    )
    return {"detail": "VERIFICATION_SUCCESSFUL_QR_SENT"}


@router.get(
    "/verify-email-link",
    summary="Endpoint público 1-clic para validación desde correo",
)
def verify_email_link_get(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        student_id_str = payload.get("sub")
        if not student_id_str:
            raise HTTPException(status_code=400, detail="INVALID_TOKEN")
    except JWTError:
        raise HTTPException(status_code=400, detail="INVALID_OR_EXPIRED_TOKEN")

    repo = StudentRepo()
    student = repo.get_by_id(db, student_id_str)
    if not student:
        raise HTTPException(status_code=404, detail="STUDENT_NOT_FOUND")

    from app.services.qr_service import generate_qr_base64_for_checkin
    from app.services.email_service import send_qr_code_email

    qr_base64 = generate_qr_base64_for_checkin(student.id, student.matricula)
    
    send_qr_code_email(
        to_email=student.email,
        student_name=student.nombre,
        qr_base64=qr_base64
    )
    
    return RedirectResponse(url="http://127.0.0.1:5500/Estudiante/gracias_registro.html")


@router.post(
    "/becario/scan-qr",
    response_model=CheckinResponse,
    status_code=status.HTTP_200_OK,
    summary="Becario hace checkin escaneando el QR",
)
def becario_scan_qr(
    payload: QRCheckinRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "intern"])),
):
    import json
    from uuid import UUID
    from app.services.checkin_service import checkin_student_by_qr

    try:
        qr_data = json.loads(payload.qr_payload)
        student_id_str = qr_data.get("student_id")
        action = qr_data.get("action")
        
        if not student_id_str or action != "checkin":
            raise ValueError()
            
        student_id = UUID(student_id_str)
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="INVALID_QR_PAYLOAD")

    return checkin_student_by_qr(
        student_id=student_id,
        db=db,
        method=payload.method,
        device=payload.device,
    )