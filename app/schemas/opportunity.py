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