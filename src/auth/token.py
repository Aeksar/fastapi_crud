from datetime import datetime, timedelta, timezone
import uuid
import jwt

from src.settings import settings


def encode_jwt(
    payload: dict,
    private_key: str | None = None,
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
) -> str:
    private_key = private_key or settings.auth.load_private()
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    return jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )


def decode_jwt(
        token: str | bytes,
        public_key: str | None = None,
        algorithm: str = settings.auth.algorithm,
) -> dict:
    public_key = public_key or settings.auth.load_public()
    return jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )