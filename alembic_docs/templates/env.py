"""Alembic async environment configuration for Ghana Motivation Backend.

Configured to dynamically extract database connection URL and SQLAlchemy
metadata from the application core, ensuring 100% synchronization between
codebase models and database migrations.
"""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ----------------------------------------------------------------------
# 1. Project Path Resolution & Dynamic Imports
# ----------------------------------------------------------------------
# Ensure project root is in sys.path so we can import GhanaMotivationApp
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.database.base import Base

# Model Registry Import:
# Explicitly import all domain models to ensure Base.metadata is fully populated
# and relationships across modules are resolved for autogenerate detection.
from GhanaMotivationApp.modules.auth.model import RefreshSession  # noqa: F401
from GhanaMotivationApp.modules.user.model import User              # noqa: F401
from GhanaMotivationApp.modules.payment.model import Payment        # noqa: F401
from GhanaMotivationApp.modules.subscription.model import Subscription  # noqa: F401
from GhanaMotivationApp.modules.quote.model import Quote            # noqa: F401


# ----------------------------------------------------------------------
# 2. Alembic Configuration & Logging
# ----------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Dynamically bind the application's configured DATABASE_URL
# This ensures migrations always run against the active environment database
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Provide SQLAlchemy model metadata to Alembic for autogenerate support
target_metadata = Base.metadata


# ----------------------------------------------------------------------
# 3. Offline Migration Execution
# ----------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available. Calls to context.execute()
    here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ----------------------------------------------------------------------
# 4. Online Async Migration Execution
# ----------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    """Synchronously executes migrations within the connection context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Initializes an asynchronous engine and runs migrations."""
    # Build engine configuration from alembic.ini section
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using asyncio event loop."""
    asyncio.run(run_async_migrations())


# ----------------------------------------------------------------------
# 5. Entry Point Dispatcher
# ----------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
