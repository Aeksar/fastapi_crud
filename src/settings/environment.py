from pydantic_settings import BaseSettings
from pydantic import ConfigDict


GLOBAL_PREFIX = "/api/v1"

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    TEST_DB_HOST: str
    TEST_DB_NAME: str
    
    REDIS_PORT: str
    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_USERNAME: str
    REDIS_DB: str

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def TEST_ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.TEST_DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"
    
    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.TEST_DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"

    
    model_config = ConfigDict(
        env_file = ".env"
    )

settings = Settings()