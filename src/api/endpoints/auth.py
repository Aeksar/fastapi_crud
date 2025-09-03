from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm


from src.repositories.user import UserService, get_user_service, get_user_repo, BaseUserRepository
from src.auth.create import create_access_token, create_refresh_token
from src.auth.token import decode_jwt
from src.settings import settings
from src.exc.api import InvalidTokenException
from src.api.models.auth import TokenInfo



auth_router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_NAME = "access_token"
REFRESH_TOKEN_NAME = "refresh_token"

@auth_router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    user = await service.authenticate(form_data.username, form_data.password)
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response.set_cookie(
        ACCESS_TOKEN_NAME,
        access_token,
        max_age=settings.auth.access_token_expire_minutes,
        httponly=True,
        secure=True
    )
    response.set_cookie(
        REFRESH_TOKEN_NAME,
        refresh_token,
        max_age=settings.auth.refresh_token_expire_minutes,
        httponly=True,
        secure=True
    )
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@auth_router.get(
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

