from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import get_current_student, require_roles
from app.core.config import settings
from app.core.db import get_db
from app.repositories.student_repo import StudentRepo
from app.schemas.checkin import CheckinResponse, QRCheckinRequest
from app.schemas.student_views import StudentUpdateSchema
from app.schemas.student_views import (
    StudentActiveEnrollmentResponse,
    StudentCheckinStatusResponse,
    StudentEnrollmentHistoryResponse,
    StudentMeResponse,
)
from app.services.checkin_service import checkin_student_by_qr
from app.services.student_view_service import (
    get_current_student_active_enrollment,
    get_current_student_checkin_status,
    get_current_student_enrollment_history,
    get_current_student_profile,
)

router = APIRouter(prefix="/students", tags=["students"])


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


@router.patch("/me", status_code=status.HTTP_200_OK)
def update_profile(
    payload: StudentUpdateSchema,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    repo = StudentRepo()
    updated_student = repo.update(
        db,
        student_id=current_student.id,
        data=payload.dict(exclude_unset=True),
    )

    if updated_student:
        from app.core.security import create_access_token
        from app.services.email_service import send_updated_registration_confirmation

        verify_token = create_access_token(
            subject=str(updated_student.id),
            role="verify",
            token_type="verify",
        )

        send_updated_registration_confirmation(
            to_email=updated_student.email,
            student_name=updated_student.nombre,
            matricula=updated_student.matricula,
            password=payload.password,
            verify_token=verify_token,
        )

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
    from app.services.email_service import send_qr_code_email
    from app.services.qr_service import generate_qr_base64_for_checkin

    qr_base64 = generate_qr_base64_for_checkin(
        current_student.id,
        current_student.matricula,
    )

    send_qr_code_email(
        to_email=current_student.email,
        student_name=current_student.nombre,
        qr_base64=qr_base64,
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

    from app.services.email_service import send_qr_code_email
    from app.services.qr_service import generate_qr_base64_for_checkin

    qr_base64 = generate_qr_base64_for_checkin(student.id, student.matricula)

    send_qr_code_email(
        to_email=student.email,
        student_name=student.nombre,
        qr_base64=qr_base64,
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>¡Registro Confirmado!</title>
    </head>
    <body>
        <h1>¡Registro Confirmado!</h1>
        <p>Tu información ha sido verificada exitosamente.</p>
        <img src="data:image/png;base64,{qr_base64}" alt="Tu Código QR" />
        <p>Nombre: {student.nombre} {student.apellido}</p>
        <p>Matrícula: {student.matricula}</p>
        <p>Correo: {student.email}</p>
        <p>También te hemos enviado este QR a {student.email}.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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