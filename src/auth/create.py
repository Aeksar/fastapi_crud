import secrets
from fastapi import Response

from src.utils.enums import TokenType
from src.api.models.user import UserResponse
from src.api.models.auth import TokenInfo
from src.auth.token import encode_jwt
from src.settings import settings
from src.auth.token import set_tokens_to_cookie


def create_jwt(
    token_type: TokenType,
    token_data: dict,
    expire_minutes: int = settings.auth.access_token_expire_minutes
) -> str:
    payload = {"type": token_type}
    payload.update(token_data)
    return encode_jwt(payload, expire_minutes=expire_minutes)


def create_access_token(user: UserResponse):
    data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name
    }
    return create_jwt(
        token_type=TokenType.ACCESS,
        token_data=data
    )

def create_refresh_token(user: UserResponse):
    data = {"sub": str(user.id)}
    return create_jwt(
        token_type=TokenType.REFRESH,
        token_data=data,
        expire_minutes=settings.auth.refresh_token_expire_minutes
    )

def create_verification_token(user: UserResponse):
    data = {"sub": str(user.id)}
    return create_jwt(
        token_type=TokenType.VERIFICATION,
        token_data=data,
        expire_minutes=settings.auth.verification_token_expire_minutes
    )



