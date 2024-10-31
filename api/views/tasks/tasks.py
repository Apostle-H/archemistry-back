from pydantic import BaseModel


class DailyTaskOut(BaseModel):
    type: int
    description: str
    progress: int
    target: int
    reward_type: int
    reward: int

class SocialTaskOut(DailyTaskOut):
    target_url: str
    icon_url: str

class TaskCompleteOut(BaseModel):
    progress: int
    target: int

class TaskClaimOut(BaseModel):
    result: bool
    hard: int = 0
    soft: int = 0
    energy: int = 0
