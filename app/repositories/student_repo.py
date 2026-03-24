from sqlalchemy.orm import Session
from app.models.student import Student

class StudentRepo:
    def get_by_email(self, db: Session, email: str) -> Student | None:
        return db.query(Student).filter(Student.email == email).first()

    def get_by_matricula(self, db: Session, matricula: str) -> Student | None:
        return db.query(Student).filter(Student.matricula == matricula).first()

    def get_by_id(self, db: Session, student_id) -> Student | None:
        return db.query(Student).filter(Student.id == student_id).first()

    def create(
        self,
        db: Session,
        matricula: str,
        nombre: str,
        apellido: str,
        email: str,
        hashed_password: str,
    ) -> Student:
        student = Student(
            matricula=matricula,
            nombre=nombre,
            apellido=apellido,
            email=email,
            hashed_password=hashed_password,
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    def update(self, db: Session, student_id, data: dict) -> Student | None:
        student = self.get_by_id(db, student_id)
        if not student:
            return None
            
        if "password" in data and data["password"]:
            from app.core.security import hash_password
            student.hashed_password = hash_password(data.pop("password"))
            
        for key, value in data.items():
            setattr(student, key, value)
            
        db.commit()
        db.refresh(student)
        return student    