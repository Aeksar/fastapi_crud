from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.repositories.user import UserService, get_user_service, get_user_repo, BaseUserRepository
from src.api.models.user import UserResponse
from src.auth.create import create_access_token, create_refresh_token, create_verification_token
from src.auth.validations import get_current_user
from src.auth.token import decode_jwt, set_tokens_to_cookie, VERIFICATION_TOKEN_NAME
from src.mailing.verification import send_verification_code
from src.settings import settings
from src.exc.api import InvalidTokenException
from src.api.models.auth import TokenInfo, CodeModel
from src.utils.redis import Redis, get_redis


auth_router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_NAME = "access_token"
REFRESH_TOKEN_NAME = "refresh_token"

@auth_router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
    redis: Redis = Depends(get_redis)
):
    user = await service.authenticate(form_data.username, form_data.password)
    if user.is_verified: 
        await send_verification_code(user.email, redis)
        verification_token = create_verification_token(user)
        set_tokens_to_cookie(response, verification_token=verification_token)
        return {"message": f"send code to {user.email}"}
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    set_tokens_to_cookie(response, access_token, refresh_token)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@auth_router.post(
    "/refresh",
    response_model_exclude_none=True,
    response_model=TokenInfo,
)
async def refresh_access_token(
    request: Request,
    repo: BaseUserRepository = Depends(get_user_repo)
):
    refresh_token = request.cookies.get(REFRESH_TOKEN_NAME)
    payload = decode_jwt(refresh_token)
    user_id = payload.get("sub")
    user = await repo.get(user_id)
    token = create_access_token(user)
    return TokenInfo(access_token=token)


@auth_router.post("/2fa")
async def authenticate_from_code(
    code_model: CodeModel,
    response: Response,
    user: UserResponse = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    valid_code = await redis.get(f"2fa:{user.email}")
    if not valid_code == code_model.code:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid code")
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    set_tokens_to_cookie(response, access_token, refresh_token)
    await redis.delete(f"2fa:{user.email}")
    response.delete_cookie(VERIFICATION_TOKEN_NAME)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)

@auth_router.post("/verif-email")
async def verification_email():
    ...