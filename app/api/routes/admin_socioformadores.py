from uuid import UUID

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
    period_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """
    Recibe el CSV de proyectos, crea un usuario socioformador por empresa
    y vincula todos sus proyectos. Retorna las credenciales generadas.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un CSV.",
        )

    period_repo = PeriodRepo()
    period = period_repo.get_by_id(db, period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PERIOD_NOT_FOUND",
        )

    file_bytes = await file.read()
    results = load_csv_socioformadores(file_bytes, period_id, db)

    return {
        "total_companies": len(results),
        "credentials": results,
    }


@router.get("")
def list_socioformadores(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    """Lista todos los socioformadores con sus credenciales y número de proyectos."""
    user_repo = UserRepo(db)
    users = user_repo.get_all_socioformadores()

    return [
        {
            "id": str(u.id),
            "username": u.username,
            "plain_password": u.plain_password,
            "projects_count": len(u.partner_opportunities),
            "created_at": u.created_at,
        }
        for u in users
    ]
