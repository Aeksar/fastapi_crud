from redis.asyncio.client import Redis
from datetime import timedelta

from src.settings import settings, logger


def get_redis() -> Redis:
    
    try:
        redis_conn = Redis(
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,            
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        ) 
        logger.info(f'Successful connect to redis')
        return redis_conn
        
    except Exception as e:
        logger.error(f'Error with connect to redis: {e}')
        raise