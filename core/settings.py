from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Project settings, which are defined through an .env file
    """

    DEBUG: bool
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    TZ: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_psql_url(self, is_async: bool = True) -> str:
        return (
            f"postgresql{'+asyncpg' if is_async else ''}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


SETTINGS: Settings = Settings()
