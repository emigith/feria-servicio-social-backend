import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("periods.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ENROLLED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)