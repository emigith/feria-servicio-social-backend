from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
# Importar todos los modelos para que SQLAlchemy resuelva las relaciones
import app.models.opportunity  # noqa
import app.models.enrollment   # noqa
import app.models.period       # noqa
import app.models.student      # noqa
import app.models.checkin      # noqa
import app.models.otp_code     # noqa


def main():
    db = SessionLocal()
    try:
        users_to_seed = [
            {
                "email": "admin@feria.mx",
                "username": "admin",
                "password": "admin12345",
                "role": UserRole.admin,
            },
            {
                "email": "intern@feria.mx",
                "username": "intern",
                "password": "intern12345",
                "role": UserRole.intern,
            },
        ]

        created = 0

        for item in users_to_seed:
            existing = db.query(User).filter(User.email == item["email"]).first()
            if existing:
                if not existing.username:
                    existing.username = item["username"]
                    db.commit()
                    print(f"Username actualizado para: {item['email']}")
                else:
                    print(f"User already exists: {item['email']}")
                continue

            user = User(
                email=item["email"],
                username=item["username"],
                hashed_password=hash_password(item["password"]),
                role=item["role"],
            )
            db.add(user)
            created += 1

        db.commit()
        print(f"Seed completed. Users created: {created}")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding users: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
