from fastapi import APIRouter
from fastapi.params import Depends

from api.auth.auth import get_user
from api.controllers.user_controller import UserController
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.user.user import UserGameStateOut

router = APIRouter()

@router.get(
    path="/state",
    response_model=UserGameStateOut,
    responses={404: {"model": APIExceptionModel}}
)
async def game_state(user_in: AuthUserOut = Depends(get_user)) -> UserGameStateOut:
    return await UserController.user_game_state(user_in.user_id)