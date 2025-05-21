from typing import TypeVar, Generic, Optional, List

from pydantic import BaseModel, Field

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


class ModelResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[DataT] = None
    error: Optional[ErrorResponse] = None

    model_config = {
        "exclude_none": True
    }