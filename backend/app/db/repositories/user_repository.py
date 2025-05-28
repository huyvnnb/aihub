from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func
from sqlmodel import Session, select

from app.api.deps import SessionDep, get_db
from app.db.models import User, Role


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

    def get_all_users(self, offset: int, size: int):
        statement = (
            select(User)
            .join(Role)
            .where(User.deleted.is_(False))
            .offset(offset)
            .limit(size)
        )

        users = self.db.exec(statement).all()
        count_stmt = select(func.count()).select_from(User).where(User.deleted == False)
        total_items = self.db.exec(count_stmt).one()

        return users, total_items


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)
