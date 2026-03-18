from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EnrollmentResponse(BaseModel):
    id: UUID
    student_id: UUID
    opportunity_id: UUID
    period_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True