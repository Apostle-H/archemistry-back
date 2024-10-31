from pydantic import BaseModel


class UserGameStateOut(BaseModel):
    hard: int
    soft: int
    score: int
    energy: int
    max_energy: int
