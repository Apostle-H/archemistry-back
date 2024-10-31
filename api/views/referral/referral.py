from typing import List

from pydantic import BaseModel

from api.views.common.vec2 import Vec2

class NewReferralIn(BaseModel):
    referred_tg_id: int
    referred_by_tg_id: int

class ReferralOut(BaseModel):
    username: str
    score: int