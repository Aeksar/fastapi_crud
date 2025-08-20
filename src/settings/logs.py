import logging

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] #{levelname} {filename} ({lineno}): {message}",
    style="{",
    encoding="UTF-8",
)

logger = logging.getLogger(__name__)
handler = logging.FileHandler("logs.log")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)