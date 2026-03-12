import uuid

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("periods.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)