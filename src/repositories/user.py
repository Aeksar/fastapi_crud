from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.repositories.base.abc import BaseUserRepository
from src.repositories.base.crud import CrudRepository
from src.api.models.user import UserResponse
from src.utils.redis import Redis, get_redis
from src.db.core import get_async_session
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




def get_user_repo(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        redis: Annotated[Redis, Depends(get_redis)],
    ) -> BaseUserRepository:
    return UserRepository(session, redis)


