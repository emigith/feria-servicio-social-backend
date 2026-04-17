"""
Servicio de estadísticas para el dashboard admin.
Todas las queries son reales — sin mocks ni datos inventados.
"""

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models.checkin import Checkin
from app.models.enrollment import Enrollment
from app.models.opportunity import Opportunity
from app.models.student import Student


def get_admin_stats(db: Session) -> dict:
    # ── A. Totales base ─────────────────────────────────────────────────────
    total_checkins: int = db.query(func.count(Checkin.id)).scalar() or 0
    total_students: int = db.query(func.count(Student.id)).scalar() or 0
    active_projects: int = (
        db.query(func.count(Opportunity.id))
        .filter(Opportunity.is_active == True)  # noqa: E712
        .scalar()
        or 0
    )

    # ── B. Tasa de asistencia ────────────────────────────────────────────────
    # checkins / estudiantes registrados * 100
    attendance_rate: float = (
        round((total_checkins / total_students) * 100, 1) if total_students > 0 else 0.0
    )

    # ── C. Hora pico y flujo — filtrados por HOY ────────────────────────────
    # La feria dura 2 días: mostramos solo el día en curso para que la
    # gráfica sea relevante en tiempo real y no mezcle días anteriores.
    today_filter = func.date(Checkin.checked_in_at) == func.current_date()

    peak_row = (
        db.query(
            func.extract("hour", Checkin.checked_in_at).label("hour"),
            func.count(Checkin.id).label("cnt"),
        )
        .filter(today_filter)
        .group_by(func.extract("hour", Checkin.checked_in_at))
        .order_by(func.count(Checkin.id).desc())
        .first()
    )
    peak_hour: str | None = f"{int(peak_row.hour):02d}:00" if peak_row else None

    # ── D. Flujo por hora (gráfica de línea) — solo hoy ─────────────────────
    flow_rows = (
        db.query(
            func.extract("hour", Checkin.checked_in_at).label("hour"),
            func.count(Checkin.id).label("cnt"),
        )
        .filter(today_filter)
        .group_by(func.extract("hour", Checkin.checked_in_at))
        .order_by(func.extract("hour", Checkin.checked_in_at))
        .all()
    )
    flow_by_hour = [
        {"hour": f"{int(r.hour):02d}:00", "count": r.cnt}
        for r in flow_rows
    ]

    # ── E. Pre-registros por día (gráfica de barras) ─────────────────────────
    # Usa Student.created_at como timestamp de pre-registro
    prereg_rows = (
        db.query(
            func.date(Student.created_at).label("day"),
            func.count(Student.id).label("cnt"),
        )
        .group_by(func.date(Student.created_at))
        .order_by(func.date(Student.created_at))
        .all()
    )
    preregistrations_by_day = [
        {"date": str(r.day), "count": r.cnt}
        for r in prereg_rows
    ]

    # ── F. Top 5 proyectos por inscritos con CHECKED_IN ──────────────────────
    # JOIN con condición compuesta para no excluir proyectos con 0 inscritos
    top_rows = (
        db.query(
            Opportunity.title,
            func.count(Enrollment.id).label("cnt"),
        )
        .outerjoin(
            Enrollment,
            and_(
                Enrollment.opportunity_id == Opportunity.id,
                Enrollment.status == "CHECKED_IN",
            ),
        )
        .filter(Opportunity.is_active == True)  # noqa: E712
        .group_by(Opportunity.id, Opportunity.title)
        .order_by(func.count(Enrollment.id).desc())
        .limit(5)
        .all()
    )
    top_projects = [{"name": r.title, "registered": r.cnt} for r in top_rows]

    # ── Respuesta final ──────────────────────────────────────────────────────
    return {
        "summary": {
            "totalCheckins": total_checkins,
            "activeProjects": active_projects,
            "attendanceRate": attendance_rate,
            "peakHour": peak_hour,
        },
        "flowByHour": flow_by_hour,
        "preregistrationsByDay": preregistrations_by_day,
        "attendanceVsPreregistrations": {
            "checkins": total_checkins,
            "preregistrations": total_students,
        },
        "topProjects": top_projects,
    }
