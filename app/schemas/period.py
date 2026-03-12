from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PeriodCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    starts_at: datetime
    ends_at: datetime
    is_active: bool = False


class PeriodResponse(BaseModel):
    id: UUID
    name: str
    starts_at: datetime
    ends_at: datetime
    is_active: bool

    class Config:
        from_attributes = True