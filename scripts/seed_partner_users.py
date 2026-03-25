from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import hash_password

# Importar modelos para que SQLAlchemy registre todas las relaciones
from app.models.user import User, UserRole
from app.models.opportunity import Opportunity
from app.models.period import Period
from app.models.enrollment import Enrollment
from app.models.student import Student


def run():
    db: Session = SessionLocal()
    try:
        users = [
            {
                "email": "socio1@feria.mx",
                "password": "Socio1234!",
                "role": UserRole.socioformador,
            },
            {
                "email": "socio2@feria.mx",
                "password": "Socio1234!",
                "role": UserRole.socioformador,
            },
        ]

        for item in users:
            exists = db.query(User).filter(User.email == item["email"]).first()
            if not exists:
                user = User(
                    email=item["email"],
                    hashed_password=hash_password(item["password"]),
                    role=item["role"],
                )
                db.add(user)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()