import uuid
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.student_repo import Student, get_by_matricula, create

def register_student(matricula: str, correo: str, password: str, nombre: str, apellido: str):
    if get_by_matricula(matricula):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="STUDENT_ALREADY_EXISTS")

    student = Student(
        studentId=str(uuid.uuid4()),
        matricula=matricula,
        correo=correo,
        nombre=nombre,
        apellido=apellido,
        password_hash=hash_password(password),
    )
    create(student)

    return {"studentId": student.studentId, "matricula": student.matricula, "status": "REGISTERED"}

def login_student(matricula: str, password: str):
    student = get_by_matricula(matricula)
    if not student or not verify_password(password, student.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CREDENTIALS")

    token_data = create_access_token(subject=student.studentId)

    return {
        "token": token_data["token"],
        "expiresIn": token_data["expiresIn"],
        "student": {"studentId": student.studentId, "matricula": student.matricula, "status": "REGISTERED"},
    }
