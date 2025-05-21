from sqlmodel import Session


class RFTokenRepository:
    def __init__(self, db: Session):
        self.db = db

