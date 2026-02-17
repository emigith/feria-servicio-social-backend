from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    studentId: str
    matricula: str
    correo: str
    nombre: str
    apellido: str
    password_hash: str

_students_by_matricula: dict[str, Student] = {}

def get_by_matricula(matricula: str) -> Optional[Student]:
    return _students_by_matricula.get(matricula)

def create(student: Student) -> Student:
    _students_by_matricula[student.matricula] = student
    return student
