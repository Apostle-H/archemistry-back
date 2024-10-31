import json
import logging
import os
import hmac
import hashlib
import uuid
from urllib.parse import parse_qsl

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Request, Depends, Header
from jose import jwt

from api.errors import APIException
from api.views.auth.auth import AuthIn, InitDataIn
from api.views.auth.user import AuthUserOut

ALGORITHM = os.getenv("WALLET_API_ALGORITHM", "RS256")


def load_jwt_key(filename: str):
    with open(filename) as key_file:
        return key_file.read()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, Authorization: str = Header()):  # Swagger Authorization doc
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise APIException(status_code=401, error="Invalid authentication scheme.")
            payload = self.verify_jwt(jwt_token=credentials.credentials)
            if not payload:
                raise APIException(status_code=401, error="Invalid token or expired token.")
            return payload
        else:
            raise APIException(status_code=401, error="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str) -> bool | None:
        pub_key = load_jwt_key('./security/api.crt')  # for local dev - ../security/api.crt'
        try:
            payload = jwt.decode(jwt_token, pub_key, algorithms=['RS256'])
        except Exception as e:
            logging.error('Error verify_jwt {e=}')
            payload = None

        return payload


def get_user(token_data=Depends(JWTBearer())) -> AuthUserOut:
    user = AuthUserOut.model_validate(
        {
            "user_id": uuid.UUID(token_data['user_id']) if 'user_id' in token_data else None,
            "name": token_data['name'] if 'name' in token_data else None,
            "tg_id": int(token_data['sub']) if 'sub' in token_data else None,
            "net": token_data['net'] if 'net' in token_data else None,
            "lang": token_data['lang'] if 'lang' in token_data else None,
            "address": token_data['address'] if 'address' in token_data else None,
        }
    )

    return user


def telegram_validate(init_data: AuthIn):
    data_check_string = (
        f"auth_date={init_data.init_data_raw.auth_date}\n"
        f"query_id={init_data.init_data_raw.query_id}\n"
        f"user={init_data.init_data_raw.user.username}"
    )

    signature = hmac.new(
        str("").encode(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    return signature


def validate_telegram_init_data(init_data : AuthIn) -> InitDataIn | None:
    init_data_dict = dict(parse_qsl(init_data.init_data_raw, keep_blank_values=True))
    init_data_parsed_dict = { key: json.loads(value) if key=='user' else value for key, value in init_data_dict.items()}
    init_data_hash = init_data_dict.pop('hash', None)
    if not init_data_hash:
        return None

    bot_token = os.getenv("BOT_SECRET_KEY")
    data_check_array = [f"{key}={value}" for key, value in init_data_dict.items()]
    data_check_array.sort()
    secret_key = hmac.new(b'WebAppData', bot_token.encode('utf-8'), hashlib.sha256).digest()
    data_string = '\n'.join(data_check_array).encode('utf-8')
    calculated_hash = hmac.new(secret_key, data_string, hashlib.sha256).hexdigest()
    is_valid =  hmac.compare_digest(calculated_hash, init_data_hash)

    if not is_valid:
        return None

    return InitDataIn.model_validate(init_data_parsed_dict)