from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.deps import get_db, require_roles
from app.repositories.opportunity_repo import OpportunityRepo
from app.schemas.opportunity import (
    OpportunityAdminCreate,
    OpportunityAdminUpdate,
    OpportunityAdminResponse,
)
from app.repositories.enrollment_repo import EnrollmentRepo
from app.repositories.user_repo import UserRepo

router = APIRouter(prefix="/admin/opportunities", tags=["admin-opportunities"])

repo = OpportunityRepo()


# ---------------------------------------------------------------------------
# GET /admin/opportunities — listar todas (activas e inactivas)
# ---------------------------------------------------------------------------
@router.get("", response_model=list[OpportunityAdminResponse])
def list_all_opportunities(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    return repo.get_all(db)


# ---------------------------------------------------------------------------
# POST /admin/opportunities — crear oportunidad
# ---------------------------------------------------------------------------
@router.post("", response_model=OpportunityAdminResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityAdminCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    return repo.create(
        db=db,
        period_id=payload.period_id,
        partner_user_id=payload.partner_user_id,
        title=payload.title,
        company=payload.company,
        capacity=payload.capacity,
        description=payload.description,
        location=payload.location,
        is_active=payload.is_active,
    )


# ---------------------------------------------------------------------------
# PUT /admin/opportunities/{id} — editar oportunidad completa
# ---------------------------------------------------------------------------
@router.put("/{opportunity_id}", response_model=OpportunityAdminResponse)
def update_opportunity(
    opportunity_id: UUID,
    payload: OpportunityAdminUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    opportunity = repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OPPORTUNITY_NOT_FOUND")

    # Validar que la nueva capacidad no sea menor a los inscritos actuales
    if payload.capacity is not None:
        enrolled = opportunity.enrolled_count
        if payload.capacity < enrolled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CAPACITY_BELOW_ENROLLED_COUNT: hay {enrolled} inscritos",
            )

    return repo.update(
        db=db,
        opportunity=opportunity,
        title=payload.title,
        company=payload.company,
        capacity=payload.capacity,
        description=payload.description,
        location=payload.location,
        modality=payload.modality,
        credit_hours=payload.credit_hours,
        is_active=payload.is_active,
        partner_user_id=payload.partner_user_id,
    )


# ---------------------------------------------------------------------------
# PATCH /admin/opportunities/{id}/activate — activar
# PATCH /admin/opportunities/{id}/deactivate — desactivar
# ---------------------------------------------------------------------------
@router.patch("/{opportunity_id}/activate", response_model=OpportunityAdminResponse)
def activate_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    opportunity = repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OPPORTUNITY_NOT_FOUND")

    return repo.update(db=db, opportunity=opportunity, is_active=True)


@router.patch("/{opportunity_id}/deactivate", response_model=OpportunityAdminResponse)
def deactivate_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    opportunity = repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OPPORTUNITY_NOT_FOUND")

    return repo.update(db=db, opportunity=opportunity, is_active=False)


@router.get("/{opportunity_id}/enrollments")
def get_opportunity_enrollments(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    opportunity = repo.get_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OPPORTUNITY_NOT_FOUND")

    enrollment_repo = EnrollmentRepo()
    enrollments = enrollment_repo.get_by_opportunity(db, opportunity_id)

    return [
        {
            "enrollment_id": e.id,
            "student_id": e.student_id,
            "matricula": e.student.matricula if e.student else None,
            "nombre": e.student.nombre if e.student else None,
            "apellido": e.student.apellido if e.student else None,
            "email": e.student.email if e.student else None,
            "status": e.status,
            "created_at": e.created_at,
        }
        for e in enrollments
    ]


@router.delete("/by-period/{period_id}", status_code=status.HTTP_200_OK)
def delete_opportunities_by_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Elimina TODAS las oportunidades de un período (y sus inscripciones en cascada)."""
    deleted = repo.delete_all_by_period(db, period_id)
    return {"deleted": deleted}


@router.get("/count/by-period/{period_id}")
def count_opportunities_by_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Cuenta cuántas oportunidades existen para un período."""
    return {"count": repo.count_by_period(db, period_id)}


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    enrollment_repo = EnrollmentRepo()
    enrollment = enrollment_repo.get_by_id(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ENROLLMENT_NOT_FOUND")
    enrollment_repo.delete(db, enrollment)


@router.delete("", status_code=status.HTTP_200_OK)
def delete_all_opportunities(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Elimina TODOS los proyectos y socioformadores (y sus inscripciones en cascada)."""
    deleted_opps = repo.delete_all(db)
    user_repo = UserRepo(db)
    deleted_sf = user_repo.delete_all_socioformadores()
    return {"deleted_opportunities": deleted_opps, "deleted_socioformadores": deleted_sf}