from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Database (relative sqlite paths are resolved against the backend folder,
    # so the app finds the same DB no matter where uvicorn is started from)
    database_url: str = "sqlite:///./travelmate.db"

    # Auth
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Currency
    default_currency: str = "INR"

    # AI
    llm_provider: str = "gemini"          # "gemini" | "mock"
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.7-flash"   # fallbacks are listed in ai_service.py
    llm_timeout_seconds: int = 60
    force_demo_mode: bool = False

    # Real-data APIs (all optional)
    foursquare_api_key: str = ""
    geoapify_api_key: str = ""
    pexels_api_key: str = ""        # optional: real hotel photos (free key from pexels.com/api)

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def demo_mode(self) -> bool:
        """True when AI answers should come from built-in sample data."""
        return (
            self.force_demo_mode
            or self.llm_provider.lower() == "mock"
            or not self.gemini_api_key
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
