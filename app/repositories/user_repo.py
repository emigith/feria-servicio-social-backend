from sqlalchemy.orm import Session
from app.models.user import User

class UserRepo:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id):
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, email: str, hashed_password: str, role):
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
