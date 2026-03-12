from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.period_repo import PeriodRepo


def get_active_period(db: Session):
    repo = PeriodRepo()
    period = repo.get_active(db)

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active period found",
        )

    return period


def create_period(name: str, starts_at, ends_at, is_active: bool, db: Session):
    repo = PeriodRepo()

    if starts_at >= ends_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="starts_at must be earlier than ends_at",
        )

    if repo.get_by_name(db, name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Period name already exists",
        )

    return repo.create(
        db=db,
        name=name,
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=is_active,
    )