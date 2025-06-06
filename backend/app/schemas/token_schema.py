from typing import Optional
from uuid import UUID

from pydantic import BaseModel


#
# class TokenCreate(BaseModel):
#     user_id: UUID
#     ip_address: Optional[str]
#     user_agent: Optional[str]


class TokenPayload(BaseModel):
    sub: UUID | None = None
