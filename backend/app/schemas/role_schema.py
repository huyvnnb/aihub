from typing import Optional

from pydantic import Field, BaseModel


class RoleCreate(BaseModel):
    name: str
    desc: Optional[str] = None


class RoleResponse(BaseModel):
    name: str
    desc: Optional[str] = None

    model_config = {
        "exclude_none": True,
        "from_attributes": True
    }



