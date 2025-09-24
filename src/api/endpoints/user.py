from fastapi import APIRouter, Depends, status
from typing import Optional
from uuid import UUID

from src.repositories.auth import AuthRepository, get_auth_repo
from src.api.models.user import UserCreate, UserUpdate
from src.repositories.user import get_user_repo, UserRepository


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    service: AuthRepository = Depends(get_auth_repo),
):
    """Эндпоинт для создания нового пользователя"""
    user = await service.registration(user)
    return user


@user_router.get("/")
async def get_users(
    skip: Optional[int] = 0,
    limit: Optional[int] = 50,
    repo: UserRepository = Depends(get_user_repo),
):
    """Эндпоинт для плучения списка всех пользователей"""
    return await repo.get_list(skip, limit)


@user_router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    repo: UserRepository = Depends(get_user_repo),
):
    """Эндпоинт для получения пользователя"""
    return await repo.get(user_id)


@user_router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    repo: UserRepository = Depends(get_user_repo),
):
    """Эндпоинт для обновления пользователя"""
    return await repo.update(user_id, user)


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    repo: UserRepository = Depends(get_user_repo),
):
    """Эдпоинт для удаления пользователя"""
    return await repo.delete(user_id)


    