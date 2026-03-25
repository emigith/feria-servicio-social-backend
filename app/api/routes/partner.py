from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.db import get_db
from app.schemas.opportunity import (
    PartnerOpportunityResponse,
    PartnerOpportunityEnrollmentsResponse,
    PartnerOpportunityDashboardResponse,
)
from app.services.partner_service import (
    get_partner_opportunities,
    get_partner_opportunity_enrollments,
    get_partner_opportunity_dashboard,
)

router = APIRouter(prefix="/partner", tags=["partner"])


@router.get("/opportunities", response_model=list[PartnerOpportunityResponse])
def list_partner_opportunities(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["socioformador"])),
):
    return get_partner_opportunities(current_user.id, db)


@router.get(
    "/opportunities/{opportunity_id}/enrollments",
    response_model=PartnerOpportunityEnrollmentsResponse,
)
def list_partner_opportunity_enrollments(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["socioformador"])),
):
    return get_partner_opportunity_enrollments(current_user.id, opportunity_id, db)


@router.get(
    "/opportunities/{opportunity_id}/dashboard",
    response_model=PartnerOpportunityDashboardResponse,
)
def get_partner_dashboard(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["socioformador"])),
):
    return get_partner_opportunity_dashboard(current_user.id, opportunity_id, db)