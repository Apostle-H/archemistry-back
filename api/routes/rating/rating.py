from fastapi import APIRouter
from fastapi.params import Depends
from watchfiles import awatch

from api.auth.auth import get_user
from api.config import MATCH_SETS, GRID_SIZE_X, GRID_SIZE_Y
from api.controllers.rating_controller import RatingController
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.common.vec2 import Vec2
from api.views.rating.rating import RatingOut
from api.views.static.static import MatchConfigOut

router = APIRouter()

@router.get(
    path="/score",
    response_model=RatingOut,
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> RatingOut:
    return await RatingController.score(user_in.user_id)