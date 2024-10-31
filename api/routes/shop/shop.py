from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from api.auth.auth import get_user
from api.controllers.shop_controller import ShopController
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.shop.shop import ShopEnergyItemOut, BuyEnergyItemOut, BuyEnergyItemIn

router = APIRouter()

@router.get(
    path="/energy",
    response_model=List[ShopEnergyItemOut],
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> List[ShopEnergyItemOut]:
    return await ShopController.energy_items()

@router.post(
    path="/buy_energy",
    response_model=BuyEnergyItemOut,
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(buy_in: BuyEnergyItemIn, user_in: AuthUserOut = Depends(get_user)) -> BuyEnergyItemOut:
    return await ShopController.buy_energy_item(user_in.user_id, buy_in.type)