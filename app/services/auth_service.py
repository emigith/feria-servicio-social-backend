from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.checkin_repo import CheckinRepo
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
            detail="Ya existe un estudiante registrado con este correo.",
        )

    if repo.get_by_matricula(db, matricula):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta matrícula ya fue registrada previamente.",
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

    from app.services.email_service import send_registration_confirmation
    verify_token = create_access_token(
        subject=str(student.id),
        role="verify",
        token_type="verify",
    )
    send_registration_confirmation(
        to_email=correo,
        student_name=nombre,
        matricula=matricula,
        password=password,
        verify_token=verify_token,
    )

    return {
        "studentId": str(student.id),
        "matricula": student.matricula,
        "status": "REGISTERED",
    }


def login_student(matricula: str, password: str, db: Session):
    repo = StudentRepo()
    student = repo.get_by_matricula(db, matricula)
    
    # Permitir inicio de sesión con correo si el usuario lo pone en el form
    if not student and "@" in matricula:
        student = repo.get_by_email(db, matricula)

    if (not student) or (not verify_password(password, student.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifica que tus datos estén bien escritos.",
        )

    access_token = create_access_token(
        subject=str(student.id),
        role="student",
        token_type="student",
    )

    checkin_repo = CheckinRepo()
    checkin = checkin_repo.get_by_student(db, student.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "has_checkin": checkin is not None,
        "student": {
            "id": str(student.id),
            "matricula": student.matricula,
            "nombre": student.nombre,
            "apellido": student.apellido,
            "email": student.email,
        }
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
        "role": user.role.value,
    }