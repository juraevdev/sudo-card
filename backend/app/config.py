from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    secret_key: str = "dev-only-change-me-uznext-ecard"
    scanner_api_key: str = "dev-scanner-key"
    database_url: str = "sqlite:///./ecard.db"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"
    qr_prefix: str = "UZN"


@lru_cache
def get_settings() -> Settings:
    return Settings()
