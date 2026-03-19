from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
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

    MAIL_ENABLED: bool = False
    MAIL_FROM: str | None = None
    MAIL_HOST: str | None = None
    MAIL_PORT: int = 587
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    APP_NAME: str = "Feria de Servicio Social Backend"


settings = Settings()