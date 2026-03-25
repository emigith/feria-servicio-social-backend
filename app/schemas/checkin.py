from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CheckinResponse(BaseModel):
    student_id: UUID
    checked_in_at: datetime
    method: str | None = None
    device: str | None = None
    message: str
    access_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True


class QRCheckinRequest(BaseModel):
    qr_payload: str
    method: str | None = None
    device: str | None = None