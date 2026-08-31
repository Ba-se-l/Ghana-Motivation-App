"""Database engine configuration and lifecycle bootstrapping.

This module initializes the SQLAlchemy asynchronous database engine and provides
a utility function to bootstrap database table schemas at application startup.
"""

from sqlalchemy.ext.asyncio import create_async_engine
from .base import Base
from GhanaMotivationApp.settings import settings


# Global asynchronous SQLAlchemy engine instance bound to database URL
async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.ECHO,
)


async def create_all_tables() -> None:
    """Initializes and creates all database tables defined in ORM metadata.

    Model Registry Pattern:
        This function explicitly imports all ORM model classes before executing
        `create_all`. This ensures SQLAlchemy populates `Base.metadata` and resolves
        string-based relationship dependencies across modules, preventing mapper
        initialization errors.
    """
    # Import all domain models to register them with Base.metadata
    from GhanaMotivationApp.modules.payment import Payment         # noqa: F401
    from GhanaMotivationApp.modules.quote import Quote             # noqa: F401
    from GhanaMotivationApp.modules.subscription import Subscription # noqa: F401
    from GhanaMotivationApp.modules.user import User               # noqa: F401

    # Execute table creation synchronously within an async connection context
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)