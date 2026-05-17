import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., validation_alias="BOT_TOKEN")
    OPENAI_API_KEY: str = Field(..., validation_alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    WEBHOOK_URL: str = Field(..., validation_alias="WEBHOOK_URL")
    PORT: int = Field(default=8000, validation_alias="PORT")
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./database/detector.db", validation_alias="DATABASE_URL")
    ENVIRONMENT: str = Field(default="production", validation_alias="ENVIRONMENT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"CRITICAL CONFIGURATION ERROR: Missing required environment variables. Detailed trace: {e}")
    sys.exit(1)
