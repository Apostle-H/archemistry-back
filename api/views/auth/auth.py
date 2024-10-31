from email.policy import default

from .user import AuthUserIn
from pydantic import Field, BaseModel


class InitDataIn(BaseModel):
    auth_date: str
    hash: str
    query_id: str | None = Field(default=None)
    user: AuthUserIn


class InitTonIn(BaseModel):
    address: str = Field()
    signature: str | None = Field(default="full")


class AuthIn(BaseModel):
    init_data_raw: str | None = Field(default=None)
    referred_by_tg_id: int | None = Field(default=None)
    init_ton: InitTonIn | None = Field(default=None)
    auth_type: str = Field(default="telegram")


class AuthOut(BaseModel):
    access_token: str