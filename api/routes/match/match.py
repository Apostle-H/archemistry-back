from typing import List

from fastapi import APIRouter, Depends

from api.auth.auth import get_user
from api.controllers.match_controller import MatchController
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.match.match import MatchElementOut, MatchUserSlotOut, MatchMoveIn, MatchMoveOut, MatchClearIn, \
    MatchClearOut, MatchEnergyRestoreOut

router = APIRouter()

@router.get(
    '/all',
    response_model=List[MatchElementOut],
    responses={404: {'model': APIExceptionModel}}
)
async def all_blocks(user_in: AuthUserOut = Depends(get_user)) -> List[MatchElementOut]:
    return await MatchController.match_elements()

@router.get(
    '/user_all',
    response_model=List[MatchUserSlotOut],
    responses={404: {'model': APIExceptionModel}}
)
async def all_blocks(user_in: AuthUserOut = Depends(get_user)) -> List[MatchUserSlotOut]:
    return await MatchController.user_grid(user_in.user_id)

@router.post(
    '/restore',
    response_model=MatchEnergyRestoreOut,
    responses={404: {'model': APIExceptionModel}}
)
async def all_blocks(user_in: AuthUserOut = Depends(get_user)) -> MatchEnergyRestoreOut:
    return await MatchController.restore_energy(user_in.user_id)

@router.post(
    "/move",
    response_model=MatchMoveOut,
    responses={404: {'model': APIExceptionModel}}
)
async def move(move_in: MatchMoveIn, user_in: AuthUserOut = Depends(get_user)) -> MatchMoveOut:
    return await MatchController.move(user_in.user_id, move_in.pos, move_in.direction)

@router.post(
    "/clear",
    response_model=MatchClearOut,
    responses={404: {'model': APIExceptionModel}}
)
async def move(clear_in: MatchClearIn, user_in: AuthUserOut = Depends(get_user)) -> MatchClearOut:
    return await MatchController.clear(user_in.user_id, clear_in.clusters)

