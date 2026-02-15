from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "YPlaces Clone API"
    api_v1_prefix: str = "/api/v1"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "yplaces"
    postgres_host: str = "db"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    jwt_secret_key: str = "change-me-super-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 12

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""

    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""

    cors_origins: list[str] = [
        "https://web.telegram.org",
        "https://webapp.botfather.telegram.org",
        "http://localhost:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
