from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Project settings, which are defined through an .env file
    """

    DEBUG: bool
    TZ: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE: str
    MONGO_HOST: str
    MONGO_CONNECTION_TYPE: str = "mongodb"
    MONGO_AUTH_SOURCE: str = "admin"
    MONGO_EXTRA_URL_PARAMS: str = "retryWrites=true&w=majority"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_psql_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_mongo_url(self) -> str:
        return (
            f"{self.MONGO_CONNECTION_TYPE}://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@"
            f"{self.MONGO_HOST}/{self.MONGO_INITDB_DATABASE}?authSource={self.MONGO_AUTH_SOURCE}"
            f"&{self.MONGO_EXTRA_URL_PARAMS}"
        )


SETTINGS: Settings = Settings()
