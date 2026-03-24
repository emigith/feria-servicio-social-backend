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

def send_registration_confirmation(to_email: str, student_name: str, matricula: str, password: str, verify_token: str = "") -> None:
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
        
        <p style="font-size: 16px;">Si tu información es correcta, confirma tu pre-registro inmediatamente haciendo clic aquí:</p>
        <p>
            <a href="http://127.0.0.1:8000/api/v1/students/verify-email-link?token={verify_token}" 
               style="background-color: #10b981; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px;">
               ¡Mi información es correcta, enviar mi QR!
            </a>
        </p>

        <p style="margin-top: 30px; font-size: 14px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
           ¿Cometiste un error en tus datos (como tu nombre o correo)? Puedes editarlos ingresando con tu matrícula y contraseña aquí:
        </p>
        <p>
            <a href="http://127.0.0.1:5500/Estudiante/editar_preregistro.html" 
               style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; display: inline-block;">
               Editar información incorrecta
            </a>
        </p>
        <p style="font-size: 12px; color: #6b7280; margin-top: 25px;">
            Nota: Una vez que confirmes que tu información en el enlace de arriba es correcta, recibirás un correo con tu Código QR final de acceso al evento.
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


def send_qr_code_email(to_email: str, student_name: str, qr_base64: str) -> None:
    if not settings.MAIL_ENABLED:
        print(f"[MAIL DISABLED] Envío de QR emitido para {to_email}")
        return

    if not all([settings.MAIL_FROM, settings.MAIL_HOST, settings.MAIL_PORT, settings.MAIL_USERNAME, settings.MAIL_PASSWORD]):
        raise HTTPException(status_code=500, detail="MAIL_CONFIGURATION_INCOMPLETE")

    subject = "Tu Código QR de Acceso - Feria de Servicio Social"

    html_body = f"""
    <html>
      <body style="font-family: sans-serif; color: #333; text-align: center; padding: 20px;">
        <h2 style="color: #0f173d;">¡Información Verificada Exitosamente!</h2>
        <p>Hola <b>{student_name}</b>,</p>
        <p>Tu pre-registro está completamente validado. Por favor, <strong>guarda o toma captura de pantalla</strong> del siguiente Código QR.</p>
        <p>El día de la Feria de Servicio Social, muestra este código a un becario en la entrada para registrar tu asistencia de forma rápida e instantánea.</p>
        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 30px auto; display: inline-block; border: 1px solid #e5e7eb;">
            <img src="data:image/png;base64,{qr_base64}" alt="Código QR de Acceso" style="width: 200px; height: 200px;" />
        </div>
        <p style="color: #4b5563; font-size: 14px;">Nos vemos en la Feria.</p>
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
        print(f"[MAIL ERROR SENDING QR] {e}")