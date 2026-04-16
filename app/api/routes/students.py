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
    # -- Token expirado o inválido --
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        student_id_str = payload.get("sub")
        if not student_id_str:
            raise JWTError()
    except JWTError:
        expired_html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Enlace expirado | Feria SS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    body { font-family: 'Lexend', sans-serif; }
    .bg-blue { background: linear-gradient(-45deg,#1e3a8a,#1d4ed8,#2563eb,#3b82f6,#1d4ed8); background-size:400% 400%; animation:blueFlow 10s ease infinite; }
    @keyframes blueFlow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
  </style>
</head>
<body class="min-h-screen bg-blue flex items-center justify-center p-6">
  <div class="bg-white rounded-3xl shadow-2xl p-10 max-w-md w-full text-center">
    <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
      <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
        <path d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1 class="text-2xl font-bold text-slate-900 mb-2">Enlace expirado</h1>
    <p class="text-slate-500 mb-8">Este enlace de confirmación ya no es válido o ha expirado. Los enlaces tienen una duración limitada por seguridad.</p>
    <div class="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-8 text-left">
      <p class="text-amber-800 text-sm font-medium mb-1">¿Qué puedo hacer?</p>
      <p class="text-amber-700 text-sm">Inicia sesión nuevamente en el portal del estudiante y solicita que se reenvíe tu QR de acceso.</p>
    </div>
    <a href="http://127.0.0.1:5500/index.html"
       class="inline-block bg-yellow-600 hover:bg-yellow-700 text-white font-bold px-8 py-3 rounded-xl transition-all">
      Ir al inicio de sesión
    </a>
  </div>
</body>
</html>"""
        return HTMLResponse(content=expired_html, status_code=400)

    repo = StudentRepo()
    student = repo.get_by_id(db, student_id_str)
    if not student:
        not_found_html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Estudiante no encontrado | Feria SS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    body { font-family: 'Lexend', sans-serif; }
    .bg-blue { background: linear-gradient(-45deg,#1e3a8a,#1d4ed8,#2563eb,#3b82f6,#1d4ed8); background-size:400% 400%; animation:blueFlow 10s ease infinite; }
    @keyframes blueFlow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
  </style>
</head>
<body class="min-h-screen bg-blue flex items-center justify-center p-6">
  <div class="bg-white rounded-3xl shadow-2xl p-10 max-w-md w-full text-center">
    <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
      <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
        <path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1 class="text-2xl font-bold text-slate-900 mb-2">Estudiante no encontrado</h1>
    <p class="text-slate-500 mb-8">No encontramos ningún estudiante asociado a este enlace. Es posible que la cuenta haya sido eliminada o el enlace sea incorrecto.</p>
    <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-8 text-left">
      <p class="text-blue-800 text-sm font-medium mb-1">¿Qué puedo hacer?</p>
      <p class="text-blue-700 text-sm">Intenta registrarte nuevamente o contacta al equipo de soporte de la Feria de Servicio Social.</p>
    </div>
    <a href="http://127.0.0.1:5500/index.html"
       class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-3 rounded-xl transition-all">
      Ir al inicio de sesión
    </a>
  </div>
</body>
</html>"""
        return HTMLResponse(content=not_found_html, status_code=404)

    from app.services.email_service import send_qr_code_email
    from app.services.qr_service import generate_qr_base64_for_checkin

    qr_base64 = generate_qr_base64_for_checkin(student.id, student.matricula)

    send_qr_code_email(
        to_email=student.email,
        student_name=student.nombre,
        qr_base64=qr_base64,
    )

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>¡Registro Confirmado! | Feria SS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    body {{ font-family: 'Lexend', sans-serif; }}
    .bg-blue {{ background: linear-gradient(-45deg,#1e3a8a,#1d4ed8,#2563eb,#3b82f6,#1d4ed8); background-size:400% 400%; animation:blueFlow 10s ease infinite; }}
    @keyframes blueFlow {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
    .qr-shadow {{ box-shadow: 0 0 0 12px #dbeafe, 0 0 0 14px #2563eb; }}
  </style>
</head>
<body class="min-h-screen bg-blue flex items-center justify-center p-6">
  <div class="bg-white rounded-3xl shadow-2xl p-8 md:p-10 max-w-sm w-full text-center">

    <!-- Ícono check -->
    <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
      <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path d="M4.5 12.75l6 6 9-13.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <h1 class="text-2xl font-bold text-slate-900 mb-1">¡Registro Confirmado!</h1>
    <p class="text-slate-500 text-sm mb-7">Tu información fue verificada exitosamente.</p>

    <!-- QR -->
    <div class="flex justify-center mb-7">
      <img src="data:image/png;base64,{qr_base64}"
           alt="Tu Código QR de acceso"
           class="w-52 h-52 rounded-2xl qr-shadow" />
    </div>

    <!-- Datos del alumno -->
    <div class="bg-slate-50 rounded-2xl p-4 text-left space-y-2 mb-6">
      <div class="flex justify-between text-sm">
        <span class="text-slate-500 font-medium">Nombre</span>
        <span class="text-slate-800 font-semibold">{student.nombre} {student.apellido}</span>
      </div>
      <div class="flex justify-between text-sm">
        <span class="text-slate-500 font-medium">Matrícula</span>
        <span class="text-slate-800 font-semibold">{student.matricula}</span>
      </div>
      <div class="flex justify-between text-sm">
        <span class="text-slate-500 font-medium">Correo</span>
        <span class="text-slate-800 font-semibold truncate ml-2">{student.email}</span>
      </div>
    </div>

    <!-- Aviso correo -->
    <div class="bg-amber-50 border border-amber-200 rounded-2xl px-4 py-3">
      <p class="text-amber-800 text-xs font-medium">
        También enviamos este QR a <span class="font-bold">{student.email}</span>.<br/>
        Preséntalo el día de la feria para hacer tu check-in.
      </p>
    </div>

  </div>
</body>
</html>"""
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