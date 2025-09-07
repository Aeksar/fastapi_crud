from fastapi import APIRouter, Depends, Response, Request, HTTPException, status, Header, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from src.repositories.user import UserService, get_user_service, get_user_repo, BaseUserRepository
from src.api.models.user import UserResponse, UserUpdate
from src.auth.create import create_access_token, create_refresh_token, create_verification_token
from src.auth.validations import get_current_user, get_user_from_verification_token
from src.auth.token import decode_jwt, set_tokens_to_cookie, VERIFICATION_TOKEN_NAME
from src.mailing.verification import send_verification_code, send_verification_link, VERIFICATION_EMAIL_LINK
from src.settings import settings
from src.exc.api import NotFoundException
from src.api.models.auth import TokenInfo, CodeModel
from src.utils.redis import Redis, get_redis


auth_router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_NAME = "access_token"
REFRESH_TOKEN_NAME = "refresh_token"
VARIFICATION_EMAIL_LINK = f"{VERIFICATION_EMAIL_LINK}"


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
        print(verification_token)
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
    response: Response,
    refresh_token: str = Cookie(alias=REFRESH_TOKEN_NAME),
    repo: BaseUserRepository = Depends(get_user_repo)
):
    payload = decode_jwt(refresh_token)
    user_id = payload.get("sub")
    user = await repo.get(user_id)
    token = create_access_token(user)
    set_tokens_to_cookie(response, access_token=token)
    return TokenInfo(access_token=token)


@auth_router.post("/2fa")
async def authenticate_from_code(
    code_model: CodeModel,
    response: Response,
    # user: UserResponse = Depends(get_user_from_verification_token),
    token = Header(alias="Authenticate"),
    redis: Redis = Depends(get_redis),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_current_user_from_verify(token)
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
async def send_letter_to_verification_email(
    response: Response,
    user: UserResponse = Depends(get_current_user)
):
    if user.is_verified:
        return {"message": "Confirmation email already completed"}
    verification_token = create_verification_token(user)
    await send_verification_link(user.email, verification_token)
    set_tokens_to_cookie(response, verification_token=verification_token)
    return {"message": "send link to email"}

@auth_router.get(f"{VERIFICATION_EMAIL_LINK}" + "{token}")
async def verification_email(
    token: str,
    user: UserResponse = Depends(get_current_user),
    repo: BaseUserRepository = Depends(get_user_repo)
):
    payload = decode_jwt(token)
    if not payload.get("sub") == str(user.id):
        raise NotFoundException("Page")
    model_update = UserUpdate(is_verified=True)
    await repo.update(user.id, model_update)
    return {"message": "Success verified email"}