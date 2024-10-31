import math

from pydantic import BaseModel


class Vec2(BaseModel):
    x: int
    y: int

    def length(self) -> float:
        return math.sqrt(float(self.x)**2 + float(self.y)**2)