from typing import List

from pydantic import BaseModel

from api.views.common.vec2 import Vec2

class UserRating(BaseModel):
    username: str
    score: int
    place: int

class RatingOut(BaseModel):
    top_four: List[UserRating]
    self: UserRating

    class Config:
        arbitrary_types_allowed=True