from redis.asyncio import Redis
import secrets

from src.mailing.send import send_email

VERIFICATION_EMAIL_LINK = "/confirm-email/"

def create_code(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))

async def send_verification_code(recepient: str, redis: Redis):
    code = create_code()
    content = f"Ваш код подтверждения: {code}\n Срок действия кода 5 минут."
    subject = "Подтверждение попытки входа"
    task = await send_email(
        recepient=recepient,
        subject=subject,
        text_content=content
        )
    await redis.set(f"2fa:{recepient}", code, ex=300)

async def send_verification_link(recepient: str, token: str):
    url = "http://localhost/" + VERIFICATION_EMAIL_LINK + token
    content = f"Перейдите по этой ссылке для подтверждения вашей почты: {url}"
    subject = "Подтверждение почты"
    task = await send_email(recepient, subject, content)
