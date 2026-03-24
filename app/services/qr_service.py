import base64
import json
from io import BytesIO
from uuid import UUID

import qrcode


def generate_qr_base64_for_checkin(student_id: UUID, matricula: str) -> str:
    """
    Generates a secure or identifiable JSON payload for the student's check-in
    and returns the QR code image encoded as a base64 string.
    """
    payload = {
        "student_id": str(student_id),
        "matricula": matricula,
        "action": "checkin",
    }
    payload_str = json.dumps(payload)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to a bytes buffer
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    
    # Encode as base64
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
