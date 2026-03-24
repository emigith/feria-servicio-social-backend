import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException, status

from app.core.config import settings


def send_otp_email(to_email: str, otp_code: str, student_name: str | None = None) -> None:
    if not settings.MAIL_ENABLED:
        print(f"[MAIL DISABLED] OTP para {to_email}: {otp_code}")
        return

    if not all([
        settings.MAIL_FROM,
        settings.MAIL_HOST,
        settings.MAIL_PORT,
        settings.MAIL_USERNAME,
        settings.MAIL_PASSWORD,
    ]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MAIL_CONFIGURATION_INCOMPLETE",
        )

    subject = "Tu código OTP - Feria de Servicio Social"
    greeting = f"Hola {student_name}," if student_name else "Hola,"

    html_body = f"""
    <html>
      <body>
        <h2>Feria de Servicio Social</h2>
        <p>{greeting}</p>
        <p>Tu código OTP para ingresar al sistema es:</p>
        <h1 style="letter-spacing: 4px;">{otp_code}</h1>
        <p>Este código expira en 10 minutos.</p>
        <p>Si no solicitaste este acceso, ignora este correo.</p>
      </body>
    </html>
    """

    text_body = f"""
    Feria de Servicio Social

    {greeting}

    Tu código OTP para ingresar al sistema es: {otp_code}

    Este código expira en 10 minutos.
    Si no solicitaste este acceso, ignora este correo.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to_email

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                server.starttls()

            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())

    except Exception as e:
        print(f"[MAIL ERROR] {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FAILED_TO_SEND_EMAIL",
        )

def send_registration_confirmation(to_email: str, student_name: str, matricula: str, password: str) -> None:
    if not settings.MAIL_ENABLED:
        print(f"[MAIL DISABLED] Registro para {to_email}. Pass: {password}")
        return

    # Reutilizamos la validación de configuración que ya tienes
    if not all([settings.MAIL_FROM, settings.MAIL_HOST, settings.MAIL_PORT, settings.MAIL_USERNAME, settings.MAIL_PASSWORD]):
        raise HTTPException(status_code=500, detail="MAIL_CONFIGURATION_INCOMPLETE")

    subject = "Confirmación de Registro - Feria de Servicio Social"

    html_body = f"""
    <html>
      <body style="font-family: sans-serif; color: #333;">
        <h2 style="color: #0f173d;">¡Registro Exitoso!</h2>
        <p>Hola <b>{student_name}</b>,</p>
        <p>Te has pre-registrado correctamente para la Feria de Servicio Social 2026.</p>
        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #e5e7eb;">
            <p style="margin: 5px 0;"><strong>Matrícula:</strong> {matricula}</p>
            <p style="margin: 5px 0;"><strong>Contraseña:</strong> {password}</p>
        </div>
        <p>Si cometiste un error en tus datos, puedes editarlos ingresando con tu matrícula y contraseña aquí:</p>
        <p>
            <a href="http://127.0.0.1:5500/Estudiante/editar_preregistro.html" 
               style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; display: inline-block;">
               Editar mi información
            </a>
        </p>
        <p style="font-size: 12px; color: #6b7280; margin-top: 25px;">
            Nota: El día de la feria física, un becario te enviará un código OTP a este correo para validar tu asistencia.
        </p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())
    except Exception as e:
        print(f"[MAIL ERROR] {e}")
        # No lanzamos excepción aquí para que el registro no falle si falla el correo, 
        # pero podrías hacerlo si prefieres que sea obligatorio.