from fastapi import Depends
from sqlmodel import Session

from app.api.deps import get_db
from app.db.models import RFToken


class RFTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, token: RFToken):
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)


def get_rftoken_repo(db: Session = Depends(get_db)) -> RFTokenRepository:
    return RFTokenRepository(db=db)

