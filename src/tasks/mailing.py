from src.mailing.verification import send_verification_link, send_verification_code
from src.tasks.config import broker
from src.settings import logger


@broker.task
async def send_verification_link_task(recepient: str, token: str):
    logger.info(f"Send verification link to {recepient}")
    await send_verification_link(recepient, token)

@broker.task
async def send_verification_code_task(recepient: str, token: str):
    logger.info(f"Send verification code to {recepient}")
    await send_verification_code(recepient, token)