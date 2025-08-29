from src.repositories.base.abc import BaseUserRepository
from src.repositories.base.crud import CrudRepository
from src.api.models.user import UserResponse, UserCreate, UserCreateToDatabase
from src.utils.security import BcryptHasher, Hasher
from src.db import User


__all__ = ["UserRepository", "BaseUserRepository", "UserService"]


class UserRepository(CrudRepository, BaseUserRepository):
    model = User
    response_model = UserResponse
  

class UserService:
    def __init__(self, user_repo: BaseUserRepository, hasher: Hasher):
        self.hasher = hasher
        self.repo = user_repo

    async def registration(self, model_create: UserCreate):
        model_dict = model_create.model_dump(exclude_unset=True)
        password = model_dict.pop("password")
        hashed_password = self.hasher.hash(password)
        model_dict.update({"hashed_password": hashed_password})
        model = UserCreateToDatabase(**model_dict)
        return await self.repo.create(model)