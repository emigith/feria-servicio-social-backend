from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]  # repo root (..../app/core -> ..../repo)
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str
    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60

settings = Settings()
