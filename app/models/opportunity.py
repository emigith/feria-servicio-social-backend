import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .enrollment import Enrollment


class Opportunity(Base):
    __tablename__ = "opportunities"

    __table_args__ = (
        Index("idx_opportunities_period_id", "period_id"),
        Index("idx_opportunities_period_active", "period_id", "is_active"),
        Index("idx_opportunities_partner_user_id", "partner_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("periods.id", ondelete="CASCADE"),
        nullable=False,
    )

    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    modality: Mapped[str] = mapped_column(String(20), nullable=False, default="Presencial")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relationships ---
    period = relationship("Period", back_populates="opportunities")

    partner_user = relationship(
        "User",
        back_populates="partner_opportunities",
        foreign_keys=[partner_user_id],
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="opportunity",
        lazy="dynamic",
    )

    # --- Computed property ---
    @property
    def enrolled_count(self) -> int:
        """Cupos ocupados. Cuenta alumnos válidos para la oportunidad."""
        return self.enrollments.filter(
            Enrollment.status == "CHECKED_IN"
        ).count()

    @property
    def available_slots(self) -> int:
        """Cupos disponibles. Retorna 0 si ya está lleno (nunca negativo)."""
        return max(0, self.capacity - self.enrolled_count)

    @property
    def is_full(self) -> bool:
        return self.available_slots == 0