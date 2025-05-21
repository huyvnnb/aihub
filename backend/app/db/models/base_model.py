from datetime import datetime, timezone
from typing import Optional, TypeVar, Generic
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlmodel import SQLModel, Field

# IDType = TypeVar("IDType")


class CoreModel(SQLModel):
    id: UUID = Field(primary_key=True, nullable=False, index=True, default_factory=uuid4)

    created_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": func.now()}
    )
    deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
