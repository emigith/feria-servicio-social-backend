from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import UserLoginRequest
from app.services.auth_service import login_user

router = APIRouter(prefix="/users/auth")

@router.post("/login")
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    return login_user(
        email=str(payload.email),
        password=payload.password,
        db=db,
    )
