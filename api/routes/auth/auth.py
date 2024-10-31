import json
import logging
import uuid
import os
from urllib.parse import parse_qsl
from fastapi import APIRouter
from api.auth.auth import validate_telegram_init_data
from api.auth.token import create_token
from api.controllers.user_controller import UserController
from api.errors import APIException
from api.views.auth.auth import AuthOut, AuthIn

router = APIRouter()

DEV_LOGIN = bool(os.getenv("DEV_LOGIN", True))


@router.post("", response_model=AuthOut)
async def post_auth(init_data: AuthIn):
    logging.info(init_data)

    payload = {
        "iss": uuid.uuid4().hex
    }

    if init_data.init_ton:
        payload["address"] = init_data.init_ton.address
        payload["net"] = "testnet"

    if DEV_LOGIN:
        init_data_raw = init_data.init_data_raw
    else:
        init_data_raw = validate_telegram_init_data(init_data)

    if init_data_raw is None:
        raise APIException("Bad credentials", 401)

    init_data_dict = dict(parse_qsl(init_data.init_data_raw, keep_blank_values=True))
    init_data_parsed_dict = { key: json.loads(value) if key=='user' else value for key, value in init_data_dict.items()}
    user = init_data_parsed_dict.pop('user')

    user_id = await UserController.user_login(
        int(user.get('id')),
        bool(user.get('is_premium')),
        user.get('username'),
        init_data.referred_by_tg_id
    )

    if init_data_raw:
        payload["user_id"] = str(user_id)
        payload["name"] = user.get('username')
        payload["lang"] = user.get('language_code')
        payload["sub"] = str(user.get('id'))

    access_token = create_token(payload)

    return AuthOut(access_token=access_token)