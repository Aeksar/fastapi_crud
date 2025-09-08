from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException

from src.settings import GLOBAL_PREFIX
from src.db.models import User
from src.repositories.user import UserService, get_user_service
from src.utils.enums import UserRoleEnum


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
    
def get_user_with_permissions(permission: UserRoleEnum, user: User = Depends(get_current_user)):
    def check_permission():
        if user.role != permission or user.role != UserRoleEnum.ADMIN:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Don't have rights for this action")
        return user
    return check_permission


get_admin = get_user_with_permissions(UserRoleEnum.ADMIN)
get_redactor = get_user_with_permissions(UserRoleEnum.REDACTOR)
