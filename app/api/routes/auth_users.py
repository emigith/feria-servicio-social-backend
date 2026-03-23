from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import UserLoginRequest, UserTokenResponse
from app.services.auth_service import login_user

router = APIRouter(prefix="/users/auth", tags=["users-auth"])


@router.post("/login", response_model=UserTokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    return login_user(
        email=str(payload.email),
        password=payload.password,
        db=db,
    )