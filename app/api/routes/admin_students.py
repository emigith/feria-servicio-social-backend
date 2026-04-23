from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.api.routes.deps import get_db, require_roles
from app.models.student import Student
from app.models.enrollment import Enrollment

router = APIRouter(prefix="/admin/students", tags=["admin-students"])


@router.get("/search")
def search_students(
    q: str = Query(..., min_length=1, description="Nombre, apellido o matrícula a buscar"),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Búsqueda global de estudiantes por nombre, apellido o matrícula."""
    pattern = f"%{q}%"

    students = (
        db.query(Student)
        .options(
            joinedload(Student.enrollments).joinedload(Enrollment.opportunity)
        )
        .filter(
            or_(
                Student.nombre.ilike(pattern),
                Student.apellido.ilike(pattern),
                Student.matricula.ilike(pattern),
            )
        )
        .limit(50)
        .all()
    )

    result = []
    for s in students:
        active = next(
            (e for e in s.enrollments if e.status in ("ENROLLED", "CHECKED_IN")),
            None,
        )
        result.append({
            "student_id": str(s.id),
            "matricula": s.matricula,
            "nombre": s.nombre,
            "apellido": s.apellido,
            "email": s.email,
            "proyecto": active.opportunity.title if active and active.opportunity else None,
            "empresa": active.opportunity.company if active and active.opportunity else None,
            "status": active.status if active else None,
        })

    return result
