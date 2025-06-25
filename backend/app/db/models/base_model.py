from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, BigInteger, Identity, DateTime
from sqlmodel import SQLModel, Field


class CoreModel(SQLModel):
    id: Optional[int] = Field(
        default=None,
        sa_type=BigInteger,
        sa_column_kwargs={
            "primary_key": True,
            "index": True,
            "nullable": False,
            "autoincrement": True,
            "server_default": Identity(start=10000)
        },
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
            # "timezone": True,
        }
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
            "nullable": False,
            # "timezone": True,
        }
    )

    # deleted: bool = Field(
    #     default=False,
    #     nullable=False,
    # )
    #
    # deleted_at: Optional[datetime] = Field(
    #     default=None,
    #     sa_type=DateTime(timezone=True),
    #     nullable=True,
    # )


class DeletedModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_id: int = Field(nullable=False, index=True)
    archived_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
        }
    )