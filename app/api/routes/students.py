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
    from fastapi.responses import HTMLResponse

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
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>¡Registro Confirmado!</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', sans-serif;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #0f173d 0%, #1e3a5f 50%, #0f173d 100%);
                color: #fff;
                padding: 20px;
            }}
            .container {{
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 40px;
                max-width: 500px;
                width: 100%;
                text-align: center;
            }}
            .check-icon {{
                width: 60px; height: 60px;
                background: #10b981;
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                margin: 0 auto 20px;
                font-size: 30px;
            }}
            h1 {{ font-size: 24px; margin-bottom: 10px; color: #10b981; }}
            .subtitle {{ color: #94a3b8; margin-bottom: 25px; font-size: 14px; }}
            .qr-box {{
                background: #fff;
                border-radius: 12px;
                padding: 20px;
                display: inline-block;
                margin: 20px 0;
            }}
            .qr-box img {{ width: 200px; height: 200px; }}
            .info-card {{
                background: rgba(255,255,255,0.08);
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                text-align: left;
            }}
            .info-card p {{ margin: 5px 0; font-size: 14px; color: #cbd5e1; }}
            .info-card strong {{ color: #fff; }}
            .warning {{
                background: rgba(234, 179, 8, 0.1);
                border: 1px solid rgba(234, 179, 8, 0.3);
                border-radius: 8px;
                padding: 12px;
                margin: 20px 0;
                font-size: 13px;
                color: #fbbf24;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 25px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
                margin-top: 15px;
                transition: transform 0.2s;
            }}
            .btn:hover {{ transform: scale(1.05); }}
            .btn-primary {{
                background: #10b981;
                color: #fff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="check-icon">✓</div>
            <h1>¡Registro Confirmado!</h1>
            <p class="subtitle">Tu información ha sido verificada exitosamente</p>

            <div class="qr-box">
                <img src="data:image/png;base64,{qr_base64}" alt="Tu Código QR">
            </div>

            <div class="info-card">
                <p><strong>Nombre:</strong> {student.nombre} {student.apellido}</p>
                <p><strong>Matrícula:</strong> {student.matricula}</p>
                <p><strong>Correo:</strong> {student.email}</p>
            </div>

            <div class="warning">
                📱 <strong>¡Guarda este QR!</strong> Toma una captura de pantalla o revísalo en tu correo.
                Preséntalo el día de la Feria de Servicio Social para registrar tu asistencia.
            </div>

            <p style="font-size: 13px; color: #94a3b8; margin-top: 10px;">
                También te hemos enviado este QR a <strong>{student.email}</strong>.
            </p>

            <a href="http://127.0.0.1:5500/index.html" class="btn btn-primary">Ir a la página principal</a>
        </div>
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