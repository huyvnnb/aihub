from typing import Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel


#
# class TokenCreate(BaseModel):
#     user_id: UUID
#     ip_address: Optional[str]
#     user_agent: Optional[str]


class TokenPayload(BaseModel):
    sub: UUID | None = None


class VerifyToken:
    def __init__(self, token: str = Query(..., description="Token to verify")):
        self.token = token