from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, Depends

from src.settings import GLOBAL_PREFIX
from src.db.models import User
from src.repositories.user import UserService, get_user_service
from src.utils.enums import TokenType

token_url = f"{GLOBAL_PREFIX}/auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
 ) -> User:
    return await user_service.get_current_user(token)

async def get_user_from_verification_token(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user_from_verify(token)
    