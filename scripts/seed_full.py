"""
Seed completo: crea estudiantes realistas, inscripciones (ENROLLED y CHECKED_IN)
distribuidas en los proyectos disponibles.
"""
import sys
import random
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.models.user
import app.models.student
import app.models.period
import app.models.opportunity
import app.models.enrollment
import app.models.checkin
import app.models.otp_code

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.enrollment import Enrollment

# ── Datos realistas ────────────────────────────────────────────────────────────
NOMBRES = [
    "Valentina","Sofía","Camila","Isabela","Mariana","Fernanda","Daniela","Natalia",
    "Lucía","Gabriela","Renata","Alejandra","Paulina","Valeria","Andrea","Ximena",
    "Regina","Emilia","Diana","Karla","Santiago","Sebastián","Mateo","Nicolás","Andrés",
    "Rodrigo","Diego","Emilio","Alejandro","Fernando","Roberto","Miguel","Jorge","Pablo",
    "Eduardo","Daniel","Ricardo","Arturo","Javier","Manuel","Luis","Carlos","Óscar",
    "Adrián","Héctor","Iván","Raúl","Ernesto","Tomás","Felipe",
]

APELLIDOS = [
    "García","Martínez","López","González","Hernández","Pérez","Ramírez","Torres",
    "Flores","Rivera","Morales","Jiménez","Ruiz","Vargas","Mendoza","Reyes",
    "Castro","Gutiérrez","Díaz","Ortiz","Sánchez","Vega","Castillo","Ramos",
    "Luna","Salinas","Herrera","Delgado","Aguilar","Navarro","Medina","Rojas",
    "Fuentes","Cruz","Ávila","Contreras","Guerrero","Chávez","Montes","Campos",
]

def gen_matricula(used: set) -> str:
    while True:
        m = f"A0{random.randint(1000000, 1999999)}"
        if m not in used:
            used.add(m)
            return m

def main():
    db = SessionLocal()
    try:
        opps = db.query(Opportunity).all()
        if not opps:
            print("ERROR: No hay oportunidades. Carga un CSV primero.")
            return

        # Agrupar oportunidades por period_id
        by_period: dict[str, list] = {}
        for o in opps:
            pid = str(o.period_id)
            by_period.setdefault(pid, []).append(o)

        periods = list(by_period.keys())
        print(f"Períodos: {len(periods)}  |  Oportunidades totales: {len(opps)}")

        # ── Crear 60 estudiantes ──────────────────────────────────────────────
        used_matriculas: set[str] = set(
            r[0] for r in db.query(Student.matricula).all()
        )
        new_students = []
        used_pairs: set[tuple] = set()  # (nombre, apellido) para evitar duplicados exactos

        for _ in range(60):
            nombre   = random.choice(NOMBRES)
            apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            while (nombre, apellido) in used_pairs:
                nombre   = random.choice(NOMBRES)
                apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            used_pairs.add((nombre, apellido))

            mat   = gen_matricula(used_matriculas)
            email = f"{mat.lower()}@tec.mx"
            s = Student(
                matricula=mat,
                nombre=nombre,
                apellido=apellido,
                email=email,
                hashed_password=hash_password("Demo1234!"),
            )
            db.add(s)
            new_students.append(s)

        db.flush()
        print(f"Creados {len(new_students)} estudiantes.")

        # ── Inscribir en proyectos ─────────────────────────────────────────────
        # Rastrear (student_id, period_id) ya inscritos para respetar la restricción
        existing: set[tuple] = set(
            (str(r.student_id), str(r.period_id))
            for r in db.query(Enrollment.student_id, Enrollment.period_id).all()
        )

        enrolled_count  = 0
        checkin_count   = 0

        for student in new_students:
            # Inscribir en 1-2 períodos distintos
            periods_to_enroll = random.sample(periods, k=min(random.randint(1, 2), len(periods)))

            for pid in periods_to_enroll:
                key = (str(student.id), pid)
                if key in existing:
                    continue

                opp = random.choice(by_period[pid])
                status = random.choices(
                    ["ENROLLED", "CHECKED_IN"],
                    weights=[45, 55],  # mayoría con check-in para que el dashboard se vea lleno
                )[0]

                enr = Enrollment(
                    student_id=student.id,
                    opportunity_id=opp.id,
                    period_id=opp.period_id,
                    status=status,
                )
                db.add(enr)
                existing.add(key)

                if status == "ENROLLED":
                    enrolled_count += 1
                else:
                    checkin_count += 1

        db.commit()
        print(f"Inscripciones ENROLLED:   {enrolled_count}")
        print(f"Inscripciones CHECKED_IN: {checkin_count}")
        print(f"Total inscripciones:      {enrolled_count + checkin_count}")
        print("Seed completado.")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
