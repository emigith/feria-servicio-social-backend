from uuid import UUID

from pydantic import BaseModel


class OpportunityResponse(BaseModel):
    id: UUID
    period_id: UUID
    title: str
    description: str | None
    company: str
    location: str | None
    capacity: int
    is_active: bool

    class Config:
        from_attributes = True


class OpportunityDetailResponse(BaseModel):
    id: UUID
    period_id: UUID
    title: str
    description: str | None
    company: str
    location: str | None
    capacity: int
    is_active: bool

    class Config:
        from_attributes = True
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OpportunityCreateRequest(BaseModel):
    period_id: UUID
    title: str
    description: str | None = None
    company: str
    location: str | None = None
    capacity: int
    is_active: bool = True


class OpportunityUpdateRequest(BaseModel):
    period_id: UUID
    title: str
    description: str | None = None
    company: str
    location: str | None = None
    capacity: int
    is_active: bool


class OpportunityAdminResponse(BaseModel):
    id: UUID
    period_id: UUID
    title: str
    description: str | None
    company: str
    location: str | None
    capacity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OpportunityEnrollmentItem(BaseModel):
    enrollment_id: UUID
    student_id: UUID
    matricula: str
    nombre: str
    apellido: str
    email: str
    status: str
    enrolled_at: datetime


class OpportunityEnrollmentsResponse(BaseModel):
    opportunity_id: UUID
    title: str
    company: str
    total_enrollments: int
    enrollments: list[OpportunityEnrollmentItem]