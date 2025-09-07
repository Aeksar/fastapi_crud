from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import jwt

from src.repositories.base.abc import BaseUserRepository
from src.repositories.base.crud import CrudRepository
from src.api.models.user import UserResponse, UserCreate, UserCreateToDatabase
from src.auth.token import decode_jwt
from src.auth.hash import Hasher, get_hasher
from src.utils.redis import Redis, get_redis
from src.db.core import get_async_session
from src.exc.api import InvalidTokenException, UnautorizedException
from src.utils.enums import TokenType
from src.db import User


__all__ = ["UserRepository", "BaseUserRepository", "UserService"]


class UserRepository(CrudRepository, BaseUserRepository):
    model = User
    response_model = UserResponse

    async def create(self, model_create):
        existing_user = await self.session.scalar(
            select(self.model).where(
                (self.model.email == model_create.email) | (self.model.name == model_create.name))
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с такой почтой или именем уже существует"
            )
        return await super().create(model_create)
    
    async def get_by_username(self, username):
        try:
            query = select(self.model).where(self.model.name == username)
            result = await self.session.execute(query)
            return self.response_model.model_validate(result.scalar_one())
        except SQLAlchemyError:
            return None

class UserService:
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


def get_user_repo(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        redis: Annotated[Redis, Depends(get_redis)],
    ) -> BaseUserRepository:
    return UserRepository(session, redis)

def get_user_service(
        repo: Annotated[BaseUserRepository, Depends(get_user_repo)],
        hasher: Annotated[Hasher, Depends(get_hasher)]
):
    return UserService(repo, hasher)
