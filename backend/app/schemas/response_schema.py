import math
from typing import TypeVar, Generic, Optional, List

from fastapi import Query
from pydantic import BaseModel, Field, computed_field

DataT = TypeVar('DataT')


class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: Optional[str] = None

    model_config = {
        "exclude_none": True
    }


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Mã lỗi nội bộ hoặc chung")
    message: str = Field(..., description="Thông báo lỗi tổng quan cho người dùng")
    details: Optional[List[ErrorDetail]] = Field(None, description="Chi tiết lỗi cụ thể (thường cho validation)")

    model_config = {
        "exclude_none": True
    }


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number (starting from 1)")
    size: int = Query(10, ge=1, le=100, description="Page size (number of items per page)")

    @property
    def offset(self):
        return (self.page - 1) * self.size


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1)
    total_items: int = Field(..., ge=0)

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 0
        return math.ceil(self.total_items / self.size)

    @computed_field
    @property
    def has_next_page(self) -> bool:
        return self.page < self.total_pages

    @computed_field
    @property
    def has_prev_page(self) -> bool:
        return self.page > 1

    @computed_field
    @property
    def next_page_number(self) -> Optional[int]:
        if self.has_next_page:
            return self.page + 1
        return None

    @computed_field
    @property
    def prev_page_number(self) -> Optional[int]:
        if self.has_prev_page:
            return self.page - 1
        return None


class Pagination(BaseModel, Generic[DataT]):
    data: Optional[DataT] = None
    meta: Optional[PaginationMeta] = None


class ModelResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[DataT] = None
    meta: Optional[PaginationMeta] = None
    error: Optional[ErrorResponse] = None

    model_config = {
        "exclude_none": True
    }
