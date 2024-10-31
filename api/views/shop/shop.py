from typing import List
from uuid import UUID

from pydantic import BaseModel

from api.views.common.vec2 import Vec2


class ShopEnergyItemOut(BaseModel):
    type: int
    amount: int
    cost: int

class BuyEnergyItemIn(BaseModel):
    type: int

class BuyEnergyItemOut(BaseModel):
    result: bool
    soft: int = -1
    energy: int = -1
