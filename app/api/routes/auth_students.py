from fastapi import APIRouter
from app.schemas.auth import StudentRegisterRequest, StudentLoginRequest
from app.services.auth_service import register_student, login_student

router = APIRouter(prefix="/students/auth")

@router.post("/register", status_code=201)
def register(payload: StudentRegisterRequest):
    return register_student(
        matricula=payload.matricula,
        correo=str(payload.correo),
        password=payload.password,
        nombre=payload.nombre,
        apellido=payload.apellido,
    )

@router.post("/login")
def login(payload: StudentLoginRequest):
    return login_student(matricula=payload.matricula, password=payload.password)
