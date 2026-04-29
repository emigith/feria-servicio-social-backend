import sys
from pathlib import Path
from uuid import uuid4
import random

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.db import SessionLocal
from app.core.security import hash_password

import app.models.opportunity
import app.models.enrollment
import app.models.period
import app.models.student
import app.models.checkin
import app.models.otp_code
import app.models.user

from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.enrollment import Enrollment

def main():
    db = SessionLocal()
    try:
        # 1. Obtener oportunidades existentes
        opportunities = db.query(Opportunity).all()
        if not opportunities:
            print("No hay oportunidades en la base de datos. Ejecuta seed_periods_opportunities.py primero.")
            return

        # 2. Crear algunos estudiantes de prueba si no existen
        students_data = [
            {"matricula": "A01234567", "nombre": "Juan", "apellido": "Pérez", "email": "A01234567@tec.mx"},
            {"matricula": "A01234568", "nombre": "María", "apellido": "Gómez", "email": "A01234568@tec.mx"},
            {"matricula": "A01234569", "nombre": "Carlos", "apellido": "López", "email": "A01234569@tec.mx"},
            {"matricula": "A01234570", "nombre": "Ana", "apellido": "Martínez", "email": "A01234570@tec.mx"},
            {"matricula": "A01234571", "nombre": "Luis", "apellido": "Hernández", "email": "A01234571@tec.mx"},
        ]

        students = []
        for s_data in students_data:
            student = db.query(Student).filter(Student.matricula == s_data["matricula"]).first()
            if not student:
                student = Student(
                    matricula=s_data["matricula"],
                    nombre=s_data["nombre"],
                    apellido=s_data["apellido"],
                    email=s_data["email"],
                    hashed_password=hash_password("password123")
                )
                db.add(student)
                db.flush() # Para obtener el ID
                print(f"Estudiante creado: {s_data['matricula']}")
            students.append(student)

        db.commit()

        # 3. Inscribir estudiantes en las oportunidades (aleatorio)
        created_enrollments = 0
        for student in students:
            # Seleccionar 1 oportunidad aleatoria para evitar restricción de periodo
            opp = random.choice(opportunities)
            
            # Verificar si ya está inscrito
            existing_enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.period_id == opp.period_id
            ).first()

            if not existing_enrollment:
                enrollment = Enrollment(
                    student_id=student.id,
                    opportunity_id=opp.id,
                    period_id=opp.period_id,
                    status="ENROLLED"
                )
                db.add(enrollment)
                created_enrollments += 1

        db.commit()
        print(f"Seed completado. Se crearon {created_enrollments} inscripciones de prueba.")

    except Exception as e:
        db.rollback()
        print(f"Error durante el seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
