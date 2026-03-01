from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import StudentRegisterRequest, StudentLoginRequest
from app.services.auth_service import register_student, login_student

router = APIRouter(prefix="/students/auth")

@router.post("/register", status_code=201)
def register(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    return register_student(
        matricula=payload.matricula,
        correo=str(payload.correo),
        password=payload.password,
        nombre=payload.nombre,
        apellido=payload.apellido,
        db=db,
    )

@router.post("/login")
def login(payload: StudentLoginRequest, db: Session = Depends(get_db)):
    return login_student(
        matricula=payload.matricula,
        password=payload.password,
        db=db,
    )
