from typing import Optional

from pydantic import BaseModel, constr, Field


class PermCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Permission unique name")
    display_name: Optional[str] = Field(None, max_length=100)
    desc: Optional[str] = None
    module: Optional[str] = Field(None, max_length=50)


class PermResponse(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Permission unique name")
    display_name: Optional[str] = Field(None, max_length=100)
    desc: Optional[str] = None
    module: Optional[str] = Field(None, max_length=50)

    model_config = {
        "from_attributes": True
    }