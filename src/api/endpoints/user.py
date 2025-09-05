from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from typing import Annotated, Optional
from uuid import UUID

from src.repositories import UserRepository, UserService
from src.api.models.user import UserCreate, UserUpdate, UserResponse
from src.mailing.verification import send_verification_code
from src.repositories.user import get_user_repo, get_user_service
from src.utils.redis import Redis, get_redis

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
    redis: Redis = Depends(get_redis)
):
    user = await service.registration(user)
    await send_verification_code(user.email, redis)
    return user


@user_router.get("/")
async def get_users(
    skip: Optional[int] = 0,
    limit: Optional[int] = 50,
    repo: UserRepository = Depends(get_user_repo),
):
    return await repo.get_list(skip, limit)


@user_router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    repo: UserRepository = Depends(get_user_repo),
):
    return await repo.get(user_id)


@user_router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    repo: UserRepository = Depends(get_user_repo),
):
    return await repo.update(user_id, user)


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    repo: UserRepository = Depends(get_user_repo),
):
    return await repo.delete(user_id)


    