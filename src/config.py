from typing import Any

from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
    """
    Configuration settings for the application.
    """

    DATABASE_USER: str
    DATABASE_PWD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    SENTRY_DSN: str

    ENVIRONMENT: Environment = Environment.PRODUCTION
    SITE_DOMAIN: str = "127.0.0.1"
    FRONTEND_URL: str = "https://b-express-platform.kz"
    WHATSAPP_SERVICE_URL: str = "http://localhost:8092"
    CORS_ORIGINS: list[str] = []
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]

    APP_VERSION: str = "1"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    SENDGRID_API_KEY: str
    EMAIL_CONFIRMATION_URL: str = f"{SITE_DOMAIN}/users/confirm-email/%s/%s/"

    S3_BUCKET: str

    class Config:
        env_file = ".env"


settings = Config()

DATABASE_URL = f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PWD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

app_configs: dict[str, Any] = {"title": "B-EXPRESS API", "description": "API для B-EXPRESS",
                               "swagger_ui_parameters": {"syntaxHighlight.theme": "obsidian"}}

if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
