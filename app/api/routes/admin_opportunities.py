from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.db import get_db
from app.schemas.opportunity import (
    OpportunityAdminResponse,
    OpportunityCreateRequest,
    OpportunityEnrollmentsResponse,
    OpportunityUpdateRequest,
)
from app.services.opportunity_service import (
    activate_opportunity,
    create_opportunity,
    deactivate_opportunity,
    get_opportunity_enrollments,
    update_opportunity,
)

router = APIRouter(prefix="/admin/opportunities", tags=["admin-opportunities"])


@router.post("", response_model=OpportunityAdminResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity_endpoint(
    payload: OpportunityCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN"])),
):
    return create_opportunity(
        db=db,
        period_id=payload.period_id,
        title=payload.title,
        description=payload.description,
        company=payload.company,
        location=payload.location,
        capacity=payload.capacity,
        is_active=payload.is_active,
    )


@router.put("/{opportunity_id}", response_model=OpportunityAdminResponse)
def update_opportunity_endpoint(
    opportunity_id: UUID,
    payload: OpportunityUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN"])),
):
    return update_opportunity(
        opportunity_id=opportunity_id,
        db=db,
        period_id=payload.period_id,
        title=payload.title,
        description=payload.description,
        company=payload.company,
        location=payload.location,
        capacity=payload.capacity,
        is_active=payload.is_active,
    )


@router.patch("/{opportunity_id}/activate", response_model=OpportunityAdminResponse)
def activate_opportunity_endpoint(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN"])),
):
    return activate_opportunity(opportunity_id, db)


@router.patch("/{opportunity_id}/deactivate", response_model=OpportunityAdminResponse)
def deactivate_opportunity_endpoint(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN"])),
):
    return deactivate_opportunity(opportunity_id, db)


@router.get("/{opportunity_id}/enrollments", response_model=OpportunityEnrollmentsResponse)
def get_opportunity_enrollments_endpoint(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["ADMIN"])),
):
    return get_opportunity_enrollments(opportunity_id, db)