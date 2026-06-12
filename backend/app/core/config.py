from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/trendwear_db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SUPPORT_EMAIL: str = "support@trendwear.uz"
    ADMIN_EMAIL: str = "admin@trendwear.uz"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()