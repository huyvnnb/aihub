from typing import List

from pydantic import BaseModel


class Resolution(BaseModel):
    id: int
    resolution: str
    size: float


class VideoResponse(BaseModel):
    title: str
    thumbnail: str
    duration: str
    resolutions: List[Resolution] = None

