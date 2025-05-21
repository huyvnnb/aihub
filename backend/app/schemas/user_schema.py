import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, BaseModel, constr, field_validator

from app.utils.enums import Gender


class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="user@example.com",
                            description="Địa chỉ email của người dùng, phải là duy nhất.")
    password: str = Field(
        ...,
        min_length=8,
        max_length=20,
        example="SecureP@ssw0rd!",
        description="Mật khẩu người dùng, cần có ít nhất một chữ hoa, một số và một ký tự đặc biệt."
    )
    fullname: constr(min_length=2, max_length=50) = Field(
        ..., example="John Doe",
        description="Họ và tên đầy đủ của người dùng."
    )
    dob: date = Field(
        ..., example="1990-01-15",
        description="Ngày sinh của người dùng (YYYY-MM-DD)."
    )
    gender: Gender = Field(
        ..., example=Gender.MALE,
        description="Giới tính")
    address: Optional[constr(max_length=255)] = Field(
        None, example="123 Main St, Anytown",
        description="Địa chỉ (tùy chọn).")

    @field_validator('password')
    def validate_password(cls, value):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?/~\\-]).{8,20}$"
        if not re.match(pattern, value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa, một chữ thường, một số và một ký tự đặc biệt.")
        return value


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    fullname: str
    dob: date
    address: Optional[str] = None
    avatar: Optional[str] = None
    gender: Gender
    verified: bool
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "exclude_none": True
    }
