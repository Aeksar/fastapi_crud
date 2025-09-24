from fastapi import Depends
from typing import Annotated
import jwt

from src.repositories.base.abc import BaseUserRepository
from src.api.models.user import UserResponse, UserCreate, UserCreateToDatabase
from src.auth.token import decode_jwt
from src.auth.hash import Hasher, get_hasher
from src.exc.api import InvalidTokenException, UnautorizedException
from src.repositories.user import get_user_repo
from src.repositories.base.abc import BaseAuthRepository
from src.utils.enums import TokenType
from src.db import User


class AuthRepository(BaseAuthRepository):
    def __init__(self, user_repo: BaseUserRepository, hasher: Hasher):
        self.hasher = hasher
        self.repo = user_repo

    async def registration(self, model_create: UserCreate) -> UserResponse:
        model_dict = model_create.model_dump(exclude_unset=True)
        password = model_dict.pop("password")
        hashed_password = self.hasher.hash(password)
        model_dict.update({"hashed_password": hashed_password})
        model = UserCreateToDatabase(**model_dict)
        return await self.repo.create(model)
    
    async def login(self, username: str, password: str) -> UserResponse:
        user = await self.authenticate(username, password)
        if user.is_verified:
            ...
        return user
    
    async def authenticate(self, username: str, password: str):
        user: UserResponse = await self.repo.get_by_username(username)
        if not user:
            raise UnautorizedException()
        if not self.hasher.verify(password, user.hashed_password):
            raise UnautorizedException()
        return user
    

    
    
    async def get_current_user_from_verify(self, token: str):
        return await self._get_user_from_token(token, TokenType.VERIFICATION)


    async def get_current_user(self, token: str | bytes):
        return await self._get_user_from_token(token, TokenType.ACCESS)

    
    async def _get_user_from_token(self, token: str | bytes, token_type: TokenType) -> User:
        try:
            payload = decode_jwt(token)
            if not payload.get("type") == token_type:
                raise InvalidTokenException
            
            user_id = payload.get("sub")
            return await self.repo.get(user_id)
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenException
        

def get_auth_repo(
        repo: Annotated[BaseUserRepository, Depends(get_user_repo)],
        hasher: Annotated[Hasher, Depends(get_hasher)]
) -> BaseAuthRepository:
    return AuthRepository(repo, hasher)