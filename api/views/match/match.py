from enum import Enum
from typing import List

from pydantic import Field, BaseModel
from uuid import UUID

from api.views.common.vec2 import Vec2


class MatchDirection(int, Enum):
    LEFT = 0,
    UP = 1,
    RIGHT = 2,
    DOWN = 3

class ClearColumn(BaseModel):
    x: int
    from_y: int

class MatchElementOut(BaseModel):
    id: UUID
    title: str

class MatchUserSlotOut(BaseModel):
    pos: Vec2
    element_id: UUID

    class Config:
        arbitrary_types_allowed=True

class MatchEnergyRestoreOut(BaseModel):
    energy: int
    max_energy: int

class MatchMoveIn(BaseModel):
    pos: Vec2
    direction: MatchDirection

    class Config:
        arbitrary_types_allowed=True

class MatchMoveOut(BaseModel):
    result: bool
    energy: int = -1

class MatchClearIn(BaseModel):
    clusters: List[List[Vec2]]

    class Config:
        arbitrary_types_allowed=True

class MatchClearOut(BaseModel):
    results: List[bool]
    refresh_pos: List[MatchUserSlotOut]
    soft: int
    score: int
