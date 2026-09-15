from pydantic import model_validator
from pydantic_settings import BaseSettings as Base
from pydantic_settings import SettingsConfigDict 

from GhanaMotivationApp.core.enums import EnvironmentEnum, CurrencyEnum

class Settings(Base):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


    HOST: str = "127.0.0.1"
    """The IP address or host interface to bind the Uvicorn ASGI server to."""

    PORT: int = 8000
    """The port number on which the Uvicorn ASGI server listens for requests."""

    RELOAD: bool = False
    """Boolean flag to enable automatic code reloading upon file modifications."""

    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT
    """Application runtime environment. Controls secret validation strictness."""


    API_PREFIX: str = '/api/v1'


    DATABASE_URL: str = "sqlite+aiosqlite:///./database_name.db"
    """The async database connection URL"""

    # AsyncEngineSettings
    ECHO: bool = False
    """Whether `SQLAlchemy` should log all SQL statements"""

    POOL_SIZE: int = 10
    POOL_TIMEOUT: int = 30
    MAX_OVERFLOW: int = 20
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€



    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Session â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # AsyncSessionSettings
    AUTO_FLUSH: bool = False
    """Controls `SQLAlchemy` session autoflush behavior"""

    EXPIRE_ON_COMMIT: bool = False
    """Whether to expire all instance after commit"""
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€



    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ JWT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # JWT Authentacation
    SECRET_KEY: str = "secret-key-in-production-time-in-this-place"
    """Secret key used for signing `JWT` tokens"""

    REFRESH_SECRET_KEY: str = "refresh-secret-key-in-production-time-in-this-place"
    """Separate secret key used for signing JWT refresh tokens."""

    ALGORITHM: str = 'HS256'
    """Algorithm used for `JWT` encoding"""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """Access token expiry duration in minutes"""

    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    """Refresh token expiry duration in days. Long-lived, revocable."""
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Paystack â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    PAYSTACK_SECRET_KEY: str = "YOUR_PAYSTACK_SECRET_KEY_HERE"
    PAYSTACK_PUBLIC_KEY: str = "YOUR_PAYSTACK_PUBLIC_KEY_HERE"
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"
    PAYSTACK_MODE: str = "mock"  # "mock" or "live"
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Business Rules â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    TRIAL_DAYS: int = 3
    SUBSCRIPTION_DAYS: int = 30
    SUBSCRIPTION_AMOUNT_PESEWAS: int = 1000  # 10 GHS in pesewas
    SUBSCRIPTION_CURRENCY: CurrencyEnum = CurrencyEnum.GHANA
    """Expected Paystack transaction currency code."""
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    
    # â”€â”€ CORS â”€â”€
    ALLOWED_ORIGINS: list[str] = ["*"]


    @model_validator(mode='after')
    def _validate_production_secrets(self) -> "Settings":
        """Blocks application startup if production secrets are placeholders.

        Raises:
            ValueError: If ENVIRONMENT is 'production' and any secret
                retains its default placeholder value.
        """
        if self.ENVIRONMENT != EnvironmentEnum.PRODUCTION:
            return self

        placeholders_checks: dict[str, str] = {
            'SECRET_KEY': 'secret-key-in-production-time-in-this-place',
            'REFRESH_SECRET_KEY': 'refresh-secret-key-in-production-time-in-this-place',
            'PAYSTACK_SECRET_KEY': 'YOUR_PAYSTACK_SECRET_KEY_HERE',
            'PAYSTACK_PUBLIC_KEY': 'YOUR_PAYSTACK_PUBLIC_KEY_HERE'
        }

        for field_name, forbidden_prefix in placeholders_checks.items():
            value = getattr(self, field_name)
            if value.startswith(forbidden_prefix):
                raise ValueError(
                    f"FATAL: {field_name} contans a placeholder value. "
                    f"Set a real secret in `.env` before running in production mode."
                )

        if self.ECHO:
            raise ValueError(
                "FATAL: `ECHO` must be False in production to prevent SQL statement leaks."
            )

        return self



settings = Settings()