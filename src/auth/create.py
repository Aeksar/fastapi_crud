from datetime import timedelta

from src.utils.enums import TokenType
from src.api.models.user import UserResponse
from src.auth.token import encode_jwt
from src.settings import settings


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

