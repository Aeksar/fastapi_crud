from pydantic import BaseModel, Field, ConfigDict, EmailStr, PastDate, field_validator
from typing import Optional
from uuid import UUID
import re

from src.utils.enums import UserRoleEnum


PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")

class BaseUserModel(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    birthdate: PastDate


class UserCreate(BaseUserModel):
    password: str

    @field_validator('password')
    def validate_password(cls, pwd):
        if PASSWORD_REGEX.fullmatch(pwd):
            return pwd
        raise ValueError(
                "Пароль должен содержать минимум 8 символов, "
                "включая одну заглавную букву, одну строчную букву, "
                "одну цифру и один спецсимвол"
            )


class UserCreateToDatabase(BaseUserModel):
    hashed_password: str


class UserUpdate(BaseUserModel):
    name: Optional[str] = Field(min_length=1, max_length=100, default=None)
    surname: Optional[str] = Field(min_length=1, max_length=100, default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    birthdate: Optional[PastDate] = Field(default=None)
    role: Optional[UserRoleEnum] = Field(default=None)

    @field_validator('password')
    def validate_password(cls, pwd):
        if PASSWORD_REGEX.fullmatch(pwd):
            return pwd
        raise ValueError(
                "Пароль должен содержать минимум 8 символов, "
                "включая одну заглавную букву, одну строчную букву, "
                "одну цифру и один спецсимвол"
            )


class UserResponse(BaseUserModel):
    id: UUID
    hashed_password: str
    is_active: bool
    is_verified: bool
    role: UserRoleEnum

    model_config = ConfigDict(from_attributes=True)

