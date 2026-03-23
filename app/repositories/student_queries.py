"""
student_queries.py
==================
Queries reutilizables para los endpoints GET /students/me/*.

Emilio importa las funciones que necesite directamente desde sus servicios:

    from app.repositories.student_queries import (
        get_checkin_status,
        get_active_enrollment,
        get_enrollment_history,
    )

Todas reciben una SQLAlchemy Session y un student_id (uuid.UUID).
Ninguna hace commit — solo lectura.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.checkin import Checkin
from app.models.enrollment import Enrollment
from app.models.opportunity import Opportunity
from app.models.period import Period

from app.models.student import Student

# ---------------------------------------------------------------------------
# Check-in
# ---------------------------------------------------------------------------

def get_checkin_status(db: Session, student_id: uuid.UUID) -> Optional[Checkin]:
    """
    Retorna el registro de check-in del estudiante, o None si aún no hizo check-in.

    Uso en endpoint GET /students/me/checkin-status:
        checkin = get_checkin_status(db, current_student.id)
        if checkin is None:
            return {"checked_in": False}
        return {"checked_in": True, "checked_in_at": checkin.checked_in_at}
    """
    return (
        db.query(Checkin)
        .filter(Checkin.student_id == student_id)
        .first()
    )


# ---------------------------------------------------------------------------
# Enrollment activo (periodo vigente)
# ---------------------------------------------------------------------------

def get_active_enrollment(db: Session, student_id: uuid.UUID) -> Optional[Enrollment]:
    """
    Retorna la inscripción del estudiante en el periodo activo, o None si no existe.

    Hace JOIN con Period para filtrar solo el periodo activo (is_active=True).
    Incluye la oportunidad y el periodo en el resultado (eager load via JOIN).

    Uso en endpoint GET /students/me/enrollment:
        enrollment = get_active_enrollment(db, current_student.id)
        if enrollment is None:
            raise HTTPException(404, "No tienes inscripción en el periodo activo")
    """
    return (
        db.query(Enrollment)
        .join(Period, Enrollment.period_id == Period.id)
        .join(Opportunity, Enrollment.opportunity_id == Opportunity.id)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.status == "ENROLLED",
            Period.is_active == True,
        )
        .first()
    )


# ---------------------------------------------------------------------------
# Historial completo por periodo
# ---------------------------------------------------------------------------

def get_enrollment_history(db: Session, student_id: uuid.UUID) -> list[Enrollment]:
    """
    Retorna todas las inscripciones del estudiante, ordenadas del periodo más reciente
    al más antiguo.

    Uso en endpoint GET /students/me/history:
        history = get_enrollment_history(db, current_student.id)
        return [EnrollmentHistorySchema.from_orm(e) for e in history]
    """
    return (
        db.query(Enrollment)
        .join(Period, Enrollment.period_id == Period.id)
        .join(Opportunity, Enrollment.opportunity_id == Opportunity.id)
        .filter(Enrollment.student_id == student_id)
        .order_by(Period.starts_at.desc())
        .all()
    )


# ---------------------------------------------------------------------------
# Verificaciones de negocio (las usa el servicio de inscripción)
# ---------------------------------------------------------------------------

def student_has_enrollment_in_period(
    db: Session,
    student_id: uuid.UUID,
    period_id: uuid.UUID,
) -> bool:
    """
    Verifica si el estudiante ya tiene una inscripción activa en el periodo dado.

    Uso antes de intentar inscribir:
        if student_has_enrollment_in_period(db, student.id, period.id):
            raise HTTPException(409, "ALREADY_ENROLLED_THIS_PERIOD")

    Nota: el UniqueConstraint en DB es la red de seguridad final,
    pero esta verificación previa permite devolver un error claro antes
    de llegar al constraint de Postgres.
    """
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.period_id == period_id,
            Enrollment.status == "ENROLLED",
        )
        .first()
        is not None
    )


def student_has_checkin(db: Session, student_id: uuid.UUID) -> bool:
    """
    Verifica si el estudiante ya realizó check-in.

    Uso antes de registrar un nuevo check-in:
        if student_has_checkin(db, student.id):
            raise HTTPException(409, "CHECKIN_ALREADY_EXISTS")
    """
    return (
        db.query(Checkin)
        .filter(Checkin.student_id == student_id)
        .first()
        is not None
    )



def get_student_profile(db: Session, student_id: uuid.UUID) -> Optional[Student]:
    return (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )