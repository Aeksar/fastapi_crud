from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, Depends

from src.settings import GLOBAL_PREFIX
from src.exc.api import UnautorizedException
from src.repositories.user import BaseUserRepository
from src.auth.token import decode_jwt

token_url = f"{GLOBAL_PREFIX}/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)


def get_token(
    request: Request
):
    token = request.cookies.get("access_token")
    if not token:
        raise UnautorizedException()
    return decode_jwt(token)