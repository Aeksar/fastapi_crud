from fastapi import APIRouter, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from typing import Annotated, Optional
from uuid import UUID

from src.repositories import BaseUserRepository, UserRepository, UserService
from src.api.models.user import UserCreate, UserUpdate
from src.auth.hash import get_hasher, Hasher
from src.utils.redis import get_redis
from src.db.core import get_async_session


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


auth_router = APIRouter()

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    token = await service.authenticate(form_data)
    return {"access_token": token}