from typing import List

from pydantic import BaseModel

from api.views.common.vec2 import Vec2


class MatchConfigOut(BaseModel):
    size: Vec2
    sets: List[List[Vec2]]

    class Config:
        arbitrary_types_allowed=True