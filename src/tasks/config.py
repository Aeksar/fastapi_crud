from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker
from src.settings import settings

redis_backend = RedisAsyncResultBackend(
    redis_url=settings.REDIS_URL
)

broker = RedisStreamBroker(
    url=settings.REDIS_URL
).with_result_backend(redis_backend)


