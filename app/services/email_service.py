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