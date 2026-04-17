from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, hashed_password: str, role) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_socioformador(self, username: str, plain_password: str, hashed_password: str) -> User:
        from app.models.user import UserRole
        user = User(
            username=username,
            plain_password=plain_password,
            hashed_password=hashed_password,
            role=UserRole.socioformador,
        )
        self.db.add(user)
        self.db.flush()  # obtiene el id sin hacer commit todavía
        return user

    def get_all_socioformadores(self) -> list[User]:
        from app.models.user import UserRole
        return (
            self.db.query(User)
            .filter(User.role == UserRole.socioformador)
            .order_by(User.created_at.asc())
            .all()
        )

    def delete_all_socioformadores(self) -> int:
        from app.models.user import UserRole
        deleted = (
            self.db.query(User)
            .filter(User.role == UserRole.socioformador)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted