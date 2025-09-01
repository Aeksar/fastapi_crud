from datetime import datetime, timedelta, timezone
import uuid
import jwt

from src.settings import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
) -> str:
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
        public_key: str = settings.auth.public_key.read_text(),
        algorithm: str = settings.auth.algorithm,
) -> dict:
    return jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )