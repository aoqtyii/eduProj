# app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@host:port/dbname")

    # API 前缀，与前端 vite.config.js 或 api.js 对应
    API_V1_STR: str = "/api/v1"  # 建议版本化


settings = Settings()
