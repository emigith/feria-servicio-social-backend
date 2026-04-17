from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


# --- Schemas existentes de Emilio (no tocar) ---

class OpportunityResponse(BaseModel):
    id: UUID
    period_id: UUID
    title: str
    description: str | None
    company: str
    location: str | None
    modality: str
    capacity: int
    available_slots: int
    enrolled_count: int
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
    modality: str
    capacity: int
    available_slots: int
    enrolled_count: int
    is_active: bool

    class Config:
        from_attributes = True


# --- Schemas nuevos para ADMIN ---

class OpportunityAdminCreate(BaseModel):
    """Body para crear una oportunidad nueva."""
    period_id: UUID
    partner_user_id: UUID | None = None
    title: str = Field(..., max_length=150)
    company: str = Field(..., max_length=150)
    capacity: int = Field(..., gt=0, description="Debe ser mayor a 0")
    description: str | None = None
    location: str | None = Field(None, max_length=150)
    is_active: bool = True


class OpportunityAdminUpdate(BaseModel):
    """Body para editar — todos los campos son opcionales (PATCH parcial)."""
    partner_user_id: UUID | None = None
    title: str | None = Field(None, max_length=150)
    company: str | None = Field(None, max_length=150)
    capacity: int | None = Field(None, gt=0, description="No puede ser menor a inscritos actuales")
    description: str | None = None
    location: str | None = Field(None, max_length=150)
    modality: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class OpportunityAdminResponse(BaseModel):
    """Response completo para el panel admin — incluye conteo de inscritos."""
    id: UUID
    period_id: UUID
    title: str
    description: str | None
    company: str
    location: str | None
    modality: str
    capacity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    enrolled_count: int
    available_slots: int

    class Config:
        from_attributes = True

class PartnerOpportunityResponse(BaseModel):
    id: UUID
    period_id: UUID
    title: str
    description: str | None
    company: str
    location: str | None
    capacity: int
    is_active: bool
    created_at: datetime
    enrolled_count: int
    available_slots: int

    class Config:
        from_attributes = True


class PartnerEnrollmentItem(BaseModel):
    enrollment_id: UUID
    student_id: UUID
    matricula: str
    status: str
    created_at: datetime


class PartnerOpportunityEnrollmentsResponse(BaseModel):
    opportunity_id: UUID
    title: str
    company: str
    total_enrollments: int
    enrollments: list[PartnerEnrollmentItem]


class PartnerOpportunityDashboardResponse(BaseModel):
    opportunity_id: UUID
    title: str
    company: str
    capacity: int
    enrolled_count: int
    available_slots: int
    is_full: bool
    enrollment_rate: float


class PartnerDashboardOpportunityItem(BaseModel):
    id: UUID
    title: str
    company: str
    capacity: int
    enrolled_count: int
    available_slots: int
    is_full: bool
    enrollment_rate: float

    class Config:
        from_attributes = True


class PartnerGeneralDashboardResponse(BaseModel):
    total_opportunities: int
    total_enrolled: int
    total_capacity: int
    overall_enrollment_rate: float
    opportunities: list[PartnerDashboardOpportunityItem]