from pydantic_settings import BaseSettings as Base
from pydantic_settings import SettingsConfigDict 


class Settings(Base):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


    # ──────────── Server ──────────────
    HOST: str = "127.0.0.1"
    """The IP address or host interface to bind the Uvicorn ASGI server to."""

    PORT: int = 8000
    """The port number on which the Uvicorn ASGI server listens for requests."""

    RELOAD: bool = False
    """Boolean flag to enable automatic code reloading upon file modifications."""
    # ───────────────────────────────────


    API_PREFIX: str = '/api/v1'


    # ──────────── Database ──────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./database_name.db"
    """The async database connection URL"""

    # AsyncEngineSettings
    ECHO: bool = True
    """Whether `SQLAlchemy` should log all SQL statements"""

    POOL_SIZE: int = 10
    POOL_TIMEOUT: int = 30
    MAX_OVERFLOW: int = 20
    # ───────────────────────────────────



    # ──────────── Session ──────────────
    # AsyncSessionSettings
    AUTO_FLUSH: bool = False
    """Controls `SQLAlchemy` session autoflush behavior"""

    EXPIRE_ON_COMMIT: bool = False
    """Whether to expire all instance after commit"""
    # ───────────────────────────────────



    # ──────────── JWT ──────────────
    # JWT Authentacation
    SECRET_KEY: str = "secret-key-in-production-time-in-this-place"
    """Secret key used for signing `JWT` tokens"""

    ALGORITHM: str = 'HS256'
    """Algorithm used for `JWT` encoding"""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    """Access token expiry duration in minutes"""
    # ───────────────────────────────


    # ────────────── Paystack ──────────────
    PAYSTACK_SECRET_KEY: str = "YOUR_PAYSTACK_SECRET_KEY_HERE"
    PAYSTACK_PUBLIC_KEY: str = "YOUR_PAYSTACK_PUBLIC_KEY_HERE"
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"
    PAYSTACK_MODE: str = "mock"  # "mock" or "live"
    # ───────────────────────────────


    # ────────────── Business Rules ──────────────
    TRIAL_DAYS: int = 3
    SUBSCRIPTION_DAYS: int = 30
    SUBSCRIPTION_AMOUNT_PESEWAS: int = 1000  # 10 GHS in pesewas
    # ───────────────────────────────

    
    # ── CORS ──
    ALLOWED_ORIGINS: list[str] = ["*"]


settings = Settings()