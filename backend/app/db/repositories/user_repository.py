from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select

from app.api.deps import SessionDep, get_db
from app.db.models import User
from app.schemas.user_schema import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: UUID) -> Optional[User]:
        statement = select(User).where(
            User.id == user_id, User.deleted == False
        )
        return self.db.exec(statement).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(
            User.email == email, User.deleted == False
        )
        return self.db.exec(statement).first()

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all_users(self):
        statement = select(User).where(User.deleted == False)
        return self.db.exec(statement).all()


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)
