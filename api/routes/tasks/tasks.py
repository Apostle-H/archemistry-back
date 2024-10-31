from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from watchfiles import awatch

from api.auth.auth import get_user
from api.controllers.tasks_controller import TasksController
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.tasks.tasks import DailyTaskOut, SocialTaskOut, TaskCompleteOut, TaskClaimOut

router = APIRouter()

@router.get(
    path="/daily",
    response_model=List[DailyTaskOut],
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> List[DailyTaskOut]:
    return await TasksController.daily(user_in.user_id)

@router.get(
    path="/social",
    response_model=List[SocialTaskOut],
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> List[SocialTaskOut]:
    return await TasksController.social(user_in.user_id)

@router.get(
    path="/social/validate/{task_type}",
    response_model=TaskCompleteOut,
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(task_type: int, user_in: AuthUserOut = Depends(get_user)) -> TaskCompleteOut:
    return await TasksController.validate_social(user_in.user_id, task_type)

@router.get(
    path="/rofl",
    response_model=TaskCompleteOut,
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> TaskCompleteOut:
    return await TasksController.validate_rofl(user_in.user_id)

@router.post(
    path="/claim/{task_type}",
    response_model=TaskClaimOut,
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(task_type: int, user_in: AuthUserOut = Depends(get_user)) -> TaskClaimOut:
    return await TasksController.claim(user_in.user_id, task_type)