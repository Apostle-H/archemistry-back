from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from api.auth.auth import get_user
from api.controllers.referral_controller import ReferralController
from api.errors import APIExceptionModel
from api.views.auth.user import AuthUserOut
from api.views.referral.referral import ReferralOut

router = APIRouter()

@router.get(
    path="/user_all",
    response_model=List[ReferralOut],
    responses={404: {"model": APIExceptionModel}}
)
async def match_config(user_in: AuthUserOut = Depends(get_user)) -> List[ReferralOut]:
    return await ReferralController.user_all(user_in.user_id)