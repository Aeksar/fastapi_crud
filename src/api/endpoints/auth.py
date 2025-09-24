from fastapi import APIRouter, Depends, Response, HTTPException, status, Header, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from src.repositories.user import get_user_repo, BaseUserRepository
from src.repositories.auth import get_auth_repo, AuthRepository
from src.api.models.user import UserResponse, UserUpdate
from src.auth.create import create_access_token, create_verification_token, create_tokens
from src.auth.validations import get_current_user
from src.auth.token import decode_jwt, set_tokens_to_cookie
from src.tasks import send_verification_code_task, send_verification_link_task
from src.mailing.verification import VERIFICATION_EMAIL_LINK
from src.exc.api import NotFoundException
from src.api.models.auth import TokenInfo, CodeModel
from src.utils.redis import Redis, get_redis
from src.utils.enums import TokenName


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: AuthRepository = Depends(get_auth_repo),
    redis: Redis = Depends(get_redis)
):
    """Эндпоинт для входа (выдачи токенов)"""
    user = await repo.authenticate(form_data.username, form_data.password)
    if user.is_verified: 
        await send_verification_code_task.kiq(user.email, redis)
        verification_token = create_verification_token(user)
        set_tokens_to_cookie(response, verification_token=verification_token)
        return {"message": f"send code to {user.email}"}
    return create_tokens(user, response)
    

@auth_router.post(
    "/refresh",
    response_model_exclude_none=True,
    response_model=TokenInfo,
)
async def refresh_access_token(
    response: Response,
    refresh_token: str = Cookie(alias=TokenName.REFRESH_TOKEN.value),
    repo: BaseUserRepository = Depends(get_user_repo)
):
    """Эндпоинт для обновления access_token"""
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
    token = Header(alias="Authenticate"),
    redis: Redis = Depends(get_redis),
    auth_repo: AuthRepository = Depends(get_auth_repo)
):
    """Эндпоинт для проверки кода с почты (для пользователей с подтвержденной почтой)"""
    user = await auth_repo.get_current_user_from_verify(token)
    valid_code = await redis.get(f"2fa:{user.email}")
    if not valid_code == code_model.code:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid code")
    
    token_info = create_tokens(user, response)
    await redis.delete(f"2fa:{user.email}")
    response.delete_cookie(TokenName.VERIFICATION_TOKEN.value)
    return token_info


@auth_router.post("/verif-email")
async def send_letter_to_verification_email(
    response: Response,
    user: UserResponse = Depends(get_current_user)
):
    """Эндпоинт для отправки ссылки на подтверждение почты"""
    if user.is_verified:
        return {"message": "Confirmation email already completed"}
    verification_token = create_verification_token(user)
    await send_verification_link_task.kiq(user.email, verification_token)
    set_tokens_to_cookie(response, verification_token=verification_token)
    return {"message": "send link to email"}

@auth_router.get(f"{VERIFICATION_EMAIL_LINK}" + "{token}")
async def verification_email(
    token: str,
    user: UserResponse = Depends(get_current_user),
    repo: BaseUserRepository = Depends(get_user_repo)
):
    """Эндпоинт для проверки ссылки подтверждения почты"""
    payload = decode_jwt(token)
    if not payload.get("sub") == str(user.id):
        raise NotFoundException("Page")
    model_update = UserUpdate(is_verified=True)
    await repo.update(user.id, model_update)
    return {"message": "Success verified email"}