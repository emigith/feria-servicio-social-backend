from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.student_repo import StudentRepo
from app.repositories.user_repo import UserRepo


def register_student(
    matricula: str,
    correo: str,
    password: str,
    nombre: str,
    apellido: str,
    db: Session,
):
    repo = StudentRepo()

    if repo.get_by_email(db, correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already exists (email)",
        )

    if repo.get_by_matricula(db, matricula):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already exists (matricula)",
        )

    hashed = hash_password(password)

    student = repo.create(
        db=db,
        matricula=matricula,
        nombre=nombre,
        apellido=apellido,
        email=correo,
        hashed_password=hashed,
    )

    return {
        "studentId": str(student.id),
        "matricula": student.matricula,
        "status": "REGISTERED",
    }


def login_student(matricula: str, password: str, db: Session):
    repo = StudentRepo()
    student = repo.get_by_matricula(db, matricula)

    if (not student) or (not verify_password(password, student.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        subject=str(student.id),
        role="student",
        token_type="student",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def login_user(email: str, password: str, db: Session):
    repo = UserRepo(db)
    user = repo.get_by_email(email)

    if (not user) or (not verify_password(password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        token_type="user",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }