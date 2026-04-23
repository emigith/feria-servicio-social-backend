import app.models.opportunity  # noqa
import app.models.enrollment   # noqa
import app.models.period       # noqa
import app.models.student      # noqa
import app.models.checkin      # noqa
import app.models.otp_code     # noqa
from app.core.db import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from app.models.student import Student
from app.models.enrollment import Enrollment

db = SessionLocal()
pattern = "%a%"
students = (
    db.query(Student)
    .options(joinedload(Student.enrollments).joinedload(Enrollment.opportunity))
    .filter(or_(Student.nombre.ilike(pattern), Student.apellido.ilike(pattern), Student.matricula.ilike(pattern)))
    .limit(5)
    .all()
)
print(f"Encontrados: {len(students)}")
for s in students:
    active = next((e for e in s.enrollments if e.status in ("ENROLLED", "CHECKED_IN")), None)
    proyecto = active.opportunity.title if active and active.opportunity else "Sin proyecto"
    print(f"  {s.nombre} {s.apellido} | {s.matricula} | {proyecto}")
db.close()
