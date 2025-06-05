from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select

from app.api.deps import get_db
from app.db.models import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role_by_name(self, name: str):
        statement = select(Role).where(Role.name == name)
        return self.db.exec(statement).first()

    def create_role(self, role: Role):
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role(self, role_id: int):
        statement = select(Role).where(Role.id == role_id)
        return self.db.exec(statement).first()


def get_role_repo(db: Session = Depends(get_db)) -> RoleRepository:
    return RoleRepository(db=db)