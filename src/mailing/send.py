import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.settings.environment import settings

async def send_email(
        recepient: str,
        subject: str,
        text_content: str,
        html_content: str | None = None,
):
    message = MIMEMultipart()
    message["To"] = recepient
    message["Subject"] = subject
    message["From"] = settings.mail.admin_adress

    plain_text = MIMEText(text_content, "plain", "UTF-8")
    message.attach(plain_text)
    if html_content:
        html_message = MIMEText(html_content, "html", "UTF-8")
        message.attach(html_message)

    await aiosmtplib.send(
        message,
        port=settings.mail.port,
        hostname=settings.mail.host
    )
    return True