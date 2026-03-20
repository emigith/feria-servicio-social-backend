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


# --- Schemas nuevos para ADMIN ---

class OpportunityAdminCreate(BaseModel):
    """Body para crear una oportunidad nueva."""
    period_id: UUID
    title: str = Field(..., max_length=150)
    company: str = Field(..., max_length=150)
    capacity: int = Field(..., gt=0, description="Debe ser mayor a 0")
    description: str | None = None
    location: str | None = Field(None, max_length=150)
    is_active: bool = True


class OpportunityAdminUpdate(BaseModel):
    """Body para editar — todos los campos son opcionales (PATCH parcial)."""
    title: str | None = Field(None, max_length=150)
    company: str | None = Field(None, max_length=150)
    capacity: int | None = Field(None, gt=0, description="No puede ser menor a inscritos actuales")
    description: str | None = None
    location: str | None = Field(None, max_length=150)
    is_active: bool | None = None


class OpportunityAdminResponse(BaseModel):
    """Response completo para el panel admin — incluye conteo de inscritos."""
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
    enrolled_count: int
    available_slots: int

    class Config:
        from_attributes = True
