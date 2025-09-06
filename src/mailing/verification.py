from redis.asyncio import Redis

from src.auth.create import create_code
from src.mailing.send import send_email

VERIFICATION_EMAIL_LINK = "/confirm-email/"

async def send_verification_code(recepient: str, redis: Redis):
    code = create_code()
    content = f"Ваш код подтверждения: {code}\n Срок действия кода 5 минут."
    subject = "Подтверждение попытки входа"
    await send_email(
        recepient=recepient,
        subject=subject,
        text_content=content
        )
    await redis.set(f"2fa:{recepient}", code, ex=300)

async def send_verification_link(recepient: str, token: str):
    url = "http://localhost/" + VERIFICATION_EMAIL_LINK + token
    content = f"Перейдите по этой ссылке для подтверждения вашей почты: {url}"
    subject = "Подтверждение почты"
    await send_email(recepient, subject, content)
