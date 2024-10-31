from fastapi import APIRouter
from fastapi.params import Depends

from api.auth.auth import get_user
from api.config import MATCH_SETS, GRID_SIZE_X, GRID_SIZE_Y
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.common.vec2 import Vec2
from api.views.static.static import MatchConfigOut

router = APIRouter()

@router.get(
    path="/match",
    response_model=MatchConfigOut,
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> MatchConfigOut:
    return MatchConfigOut(
        size=Vec2(x=GRID_SIZE_X, y=GRID_SIZE_Y),
        sets=MATCH_SETS
    )