from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.db import get_db
from app.repositories.user_repo import UserRepo
from app.services.socioformador_service import load_csv_socioformadores
from app.repositories.period_repo import PeriodRepo

router = APIRouter(prefix="/admin/socioformadores", tags=["admin-socioformadores"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_socioformadores_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """
    Recibe el CSV de proyectos, crea un usuario socioformador por empresa
    y vincula todos sus proyectos al período activo. Retorna las credenciales generadas.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un CSV.",
        )

    period_repo = PeriodRepo()
    period = period_repo.get_active(db)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_ACTIVE_PERIOD",
        )

    file_bytes = await file.read()
    results = load_csv_socioformadores(file_bytes, period.id, db)

    return {
        "total_companies": len(results),
        "period": period.name,
        "credentials": results,
    }


@router.get("")
def list_socioformadores(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Lista todos los socioformadores con credenciales y proyectos asignados."""
    user_repo = UserRepo(db)
    users = user_repo.get_all_socioformadores()

    result = []
    for u in users:
        opps = list(u.partner_opportunities)
        company = opps[0].company if opps else u.username
        result.append({
            "id": str(u.id),
            "company": company,
            "username": u.username,
            "plain_password": u.plain_password,
            "projects_count": len(opps),
            "created_at": u.created_at,
            "projects": [
                {
                    "id": str(o.id),
                    "project_code": o.project_code,
                    "title": o.title,
                    "modality": o.modality,
                    "credit_hours": o.credit_hours,
                    "capacity": o.capacity,
                    "enrolled_count": o.enrolled_count,
                    "available_slots": o.available_slots,
                    "is_active": o.is_active,
                }
                for o in opps
            ],
        })
    return result
