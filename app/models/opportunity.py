import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    __table_args__ = (
        Index("idx_opportunities_period_id", "period_id"),
        Index("idx_opportunities_period_active", "period_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("periods.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relationships ---
    period = relationship("Period", back_populates="opportunities")

    # AGREGADO: permite navegar opportunity.enrollments y calcular cupos
    # lazy="dynamic" evita cargar todos los enrollments en memoria si no se necesitan
    enrollments = relationship(
        "Enrollment",
        back_populates="opportunity",
        lazy="dynamic",
    )

    # --- Computed property ---
    @property
    def enrolled_count(self) -> int:
        """Cupos ocupados. Solo cuenta inscripciones activas (no canceladas)."""
        return self.enrollments.filter_by(status="ENROLLED").count()

    @property
    def available_slots(self) -> int:
        """Cupos disponibles. Retorna 0 si ya está lleno (nunca negativo)."""
        return max(0, self.capacity - self.enrolled_count)

    @property
    def is_full(self) -> bool:
        return self.available_slots == 0
 