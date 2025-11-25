from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "Invoice Matcher"
    ENV: str = "development"

    # OpenAI / LLM configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    # Database URL (SQLite for MVP)
    DATABASE_URL: str = "sqlite:///./invoice_matcher.db"

    # Storage config
    STORAGE_TYPE: str = "local"   # or "s3"
    UPLOAD_DIR: str = "./uploads"

    # S3 config (only used if STORAGE_TYPE = "s3")
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    # Upload size limit
    MAX_UPLOAD_SIZE_MB: int = 25

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
