from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole

def main():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin2@feria.mx").first()
        if existing:
            print("User already exists")
            return

        user = User(
            email="admin@feria.mx",
            hashed_password=hash_password("admin12345"),
            role=UserRole.admin,
        )
        db.add(user)
        db.commit()
        print("Admin user created")
    finally:
        db.close()

if __name__ == "__main__":
    main()
