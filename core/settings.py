import abc

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

from .mixins import EnvSettingsMixin


class ServiceSettings(EnvSettingsMixin, abc.ABC):
    @property
    @abc.abstractmethod
    def url(self) -> str:
        ...


class PSQLSettings(ServiceSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class MongoSettings(ServiceSettings):
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE: str
    MONGO_HOST: str
    MONGO_CONNECTION_TYPE: str = "mongodb"
    MONGO_AUTH_SOURCE: str = "admin"
    MONGO_EXTRA_URL_PARAMS: str = "retryWrites=true&w=majority"

    @property
    def url(self) -> str:
        return (
            f"{self.MONGO_CONNECTION_TYPE}://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@"
            f"{self.MONGO_HOST}/{self.MONGO_INITDB_DATABASE}?authSource={self.MONGO_AUTH_SOURCE}"
            f"&{self.MONGO_EXTRA_URL_PARAMS}"
        )

    @property
    def client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(self.url)


class RedisSettings(ServiceSettings):
    REDIS_HOST: str
    REDIS_PORT: str

    @property
    def url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


class AuthenticationSettings(EnvSettingsMixin):
    JWT_ACCESS_TOKEN_SECRET_KEY: str
    JWT_REFRESH_TOKEN_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MIN: int
    JWT_REFRESH_TOKEN_EXPIRE_MIN: int
    JWT_TOKEN_NAME: str = "Token"


class AppSettings(EnvSettingsMixin):
    DEBUG: bool
    TZ: str


class Settings(BaseSettings):
    """
    Project settings, which are defined through an .env file
    """

    APP: AppSettings = AppSettings()
    AUTH: AuthenticationSettings = AuthenticationSettings()
    PSQL: PSQLSettings = PSQLSettings()
    MONGO: MongoSettings = MongoSettings()
    REDIS: RedisSettings = RedisSettings()


SETTINGS: Settings = Settings()
