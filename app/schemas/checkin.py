from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OtpRequestResponse(BaseModel):
    student_id: UUID
    expires_at: datetime
    message: str

    class Config:
        from_attributes = True


class CheckinRequest(BaseModel):
    otp_code: str
    method: str | None = None
    device: str | None = None


class CheckinPublicRequest(BaseModel):
    matricula: str
    otp_code: str
    method: str | None = None
    device: str | None = None


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