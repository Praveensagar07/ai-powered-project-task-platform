"""Application configuration and environment settings."""

import os
from functools import lru_cache
from pathlib import Path
from sqlalchemy.engine import make_url


def _load_env_file(dotenv_path: Path) -> None:
    """Load key-value pairs from a .env file into os.environ if not already set."""
    if not dotenv_path.is_file():
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = val


# Load root .env or backend .env if present
_root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
_backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
_load_env_file(_root_env)
_load_env_file(_backend_env)


def normalize_database_url(raw_url: str | None) -> str:
    """Normalize and validate the database connection string.

    Supports:
    - None -> defaults to 'sqlite:///./app_data.db' for local zero-config runs.
    - Stripping accidental leading/trailing whitespace and enclosing quotes.
    - postgres://... -> postgresql+psycopg://...
    - postgresql://... -> postgresql+psycopg://...
    - postgresql+psycopg://... -> unchanged
    - sqlite://... -> unchanged

    Raises ValueError('Invalid DATABASE_URL configuration') if malformed or unsupported,
    without printing raw credentials.
    """
    if raw_url is None:
        return "sqlite:///./app_data.db"

    # Safely strip whitespace and enclosing single/double quotes
    cleaned = raw_url.strip().strip("'\"").strip()
    if not cleaned:
        raise ValueError("Invalid DATABASE_URL configuration")

    # Normalize PostgreSQL schemes to psycopg v3 dialect
    if cleaned.startswith("postgres://"):
        cleaned = "postgresql+psycopg://" + cleaned[len("postgres://"):]
    elif cleaned.startswith("postgresql://"):
        cleaned = "postgresql+psycopg://" + cleaned[len("postgresql://"):]

    # Safely validate with SQLAlchemy make_url without exposing credentials in exceptions
    try:
        parsed = make_url(cleaned)
        driver = (parsed.drivername or "").lower()
        if not (driver.startswith("sqlite") or driver.startswith("postgresql")):
            raise ValueError("Invalid DATABASE_URL configuration")
    except Exception:
        raise ValueError("Invalid DATABASE_URL configuration") from None

    return cleaned


class Settings:
    """Application settings resolved from environment variables."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "AI-Powered Project & Task Management Platform")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.api_prefix: str = os.getenv("API_PREFIX", "/api")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))

        # Database connection string with robust normalization
        raw_db_url = os.getenv("DATABASE_URL")
        self.database_url: str = normalize_database_url(raw_db_url)


        # Database pool settings
        self.db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
        self.db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() in ("true", "1", "yes")

        # JWT Authentication
        self.jwt_secret: str = os.getenv("JWT_SECRET", "super-secret-jwt-key-change-in-production-min-32-chars")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

        # AI Configuration
        self.ai_provider: str = os.getenv("AI_PROVIDER", "openai").lower()
        self.ai_api_key: str = os.getenv("AI_API_KEY", "")
        self.ai_api_base: str = os.getenv("AI_API_BASE", "https://api.openai.com/v1")
        self.ai_model: str = os.getenv("AI_MODEL", "gpt-4o-mini")

        # CORS origins parsing
        raw_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
        )
        self.cors_origins: list[str] = [
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        ]

        # Seed configuration
        self.seed_demo_data: bool = os.getenv("SEED_DEMO_DATA", "true").lower() in ("true", "1", "yes")


@lru_cache()
def get_settings() -> Settings:
    """Provide a cached singleton instance of Settings."""
    return Settings()
