from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def main():
    db = SessionLocal()
    try:
        users_to_seed = [
            {
                "email": "admin@feria.mx",
                "password": "admin12345",
                "role": UserRole.admin,
            },
            {
                "email": "intern@feria.mx",
                "password": "intern12345",
                "role": UserRole.intern,
            },
        ]

        created = 0

        for item in users_to_seed:
            existing = db.query(User).filter(User.email == item["email"]).first()
            if existing:
                print(f"User already exists: {item['email']}")
                continue

            user = User(
                email=item["email"],
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