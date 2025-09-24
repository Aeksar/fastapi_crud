from datetime import datetime, timedelta, timezone
from fastapi import Response
import uuid
import jwt

from src.settings import settings
from src.utils.enums import TokenName



def encode_jwt(
    payload: dict,
    private_key: str | None = None,
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
) -> str:
    private_key = private_key or settings.auth.load_private()
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    return jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )


def decode_jwt(
        token: str | bytes,
        public_key: str | None = None,
        algorithm: str = settings.auth.algorithm,
) -> dict:
    public_key = public_key or settings.auth.load_public()
    return jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )

def set_tokens_to_cookie(
        response: Response,
        access_token: str | None=None,
        refresh_token: str | None=None,
        verification_token: str | None=None
):
    if access_token:
        response.set_cookie(
            TokenName.ACCESS_TOKEN.value,
            access_token,
            max_age=settings.auth.access_token_expire_minutes,
            httponly=True,
            secure=True
        )
    if refresh_token:
        response.set_cookie(
            TokenName.REFRESH_TOKEN.value,
            refresh_token,
            max_age=settings.auth.refresh_token_expire_minutes,
            httponly=True,
            secure=True
        )
    if verification_token:
        response.set_cookie(
            TokenName.VERIFICATION_TOKEN.value,
            verification_token,
            max_age=settings.auth.verification_token_expire_minutes,
            httponly=True,
            secure=True
        )

