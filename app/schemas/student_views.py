from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional

from pydantic import BaseModel


class StudentMeResponse(BaseModel):
    id: UUID
    matricula: str
    nombre: str
    apellido: str
    email: str

    class Config:
        from_attributes = True


class StudentCheckinStatusResponse(BaseModel):
    has_checkin: bool
    checked_in_at: datetime | None = None
    method: str | None = None
    device: str | None = None


class StudentActiveEnrollmentResponse(BaseModel):
    enrollment_id: UUID
    opportunity_id: UUID
    period_id: UUID
    period_name: str
    title: str
    company: str
    location: str | None = None
    status: str
    enrolled_at: datetime


class StudentEnrollmentHistoryItem(BaseModel):
    enrollment_id: UUID
    opportunity_id: UUID
    period_id: UUID
    period_name: str
    title: str
    company: str
    location: str | None = None
    status: str
    enrolled_at: datetime


class StudentEnrollmentHistoryResponse(BaseModel):
    total: int
    items: list[StudentEnrollmentHistoryItem]
    

class StudentUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    matricula: Optional[str] = None
    password: Optional[str] = None