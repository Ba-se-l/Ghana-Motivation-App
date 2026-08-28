from  functools import wraps
from typing import TypeVar, ParamSpec, Callable
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .engine import async_engine
from GhanaMotivationApp.settings import settings


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=settings.AUTO_FLUSH,
    expire_on_commit=settings.EXPIRE_ON_COMMIT,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session as a FastAPI dependency.

    Creates an ``AsyncSession`` via the configured session factory.
    On successful completion of the request, the session is committed.
    On any exception, the session is rolled back and the exception is
    re-raised to propagate to the global error handler.

    Yields:
        AsyncSession: The active database session bound to the current request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


_P = ParamSpec('_P')
_R = TypeVar('_R')

def inject_session(
    func: Callable[_P, _R],
) -> Callable[_P, _R]:
    """Decorator that injects an ``AsyncSession`` as ``session`` kwarg.
    Usage::

        @inject_session
        async def create_something(session: AsyncSession, ...) -> ...:
            ...
    """

    @wraps(func)
    async def wrapper(*args: _P.args, **kw: _P.kwargs) -> _R:
        async with AsyncSessionLocal() as session:
            try:
                kw['session'] = session
                result = await func(*args, **kw)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

    return wrapper