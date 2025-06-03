from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, Column, BigInteger, Identity, DateTime, Boolean
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
        # sa_column=Column(
        #     BigInteger,
        #     Identity(start=10000),
        #     primary_key=True,
        #     index=True
        # )
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

    deleted: bool = Field(
        default=False,
        nullable=False,
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        nullable=True,
    )
