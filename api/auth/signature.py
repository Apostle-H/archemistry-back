import hashlib
import hmac
import os

from fastapi import Header, Request

from api.errors import APIException

SECRET_KEY = os.getenv("SECRET_KEY", "secret-dev-key")


async def verify_hmac(request: Request, signature: str = Header(..., alias="X-Signature")) -> str:
    body = await request.body()
    if not signature:
        raise APIException("Signature missing", 400)

    if signature.startswith("sha256="):
        signature = signature.split("=")[1]

    mac = hmac.new(SECRET_KEY.encode(), body, hashlib.sha256)

    expected_signature = mac.hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise APIException("Invalid HMAC signature", 400)

    return expected_signature
