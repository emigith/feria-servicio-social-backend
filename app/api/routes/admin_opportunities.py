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
        is_active=payload.is_active,
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
            "status": e.status,
            "created_at": e.created_at,
        }
        for e in enrollments
    ]
