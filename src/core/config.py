from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_ignore_empty=True,
        extra="ignore",
        env_file_encoding="utf-8",
    )
    ENVIRONMENT: Literal["test", "local", "staging", "production"] = "local"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "SECRET_KEY"
    ALGORITHM: str = "HS256"

    # POSTGRES_SERVER: str
    # POSTGRES_PORT: int = 5432
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str = ""


settings = Settings()
