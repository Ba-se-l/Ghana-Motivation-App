"""Quote domain service layer.

Provides high-level business orchestration for retrieving daily, random,
and batch motivational quotes from the database repository.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.core import NotFoundException
from .repo import QuoteRepository
from .model import Quote


async def get_today_quote(session: AsyncSession) -> Quote:
    """Retrieves the motivational quote for today based on current UTC day-of-year.

    Args:
        session: The active asynchronous database session.

    Returns:
        The `Quote` model instance corresponding to current day of year (1-365).

    Raises:
        NotFoundException: If no quote exists for the current day.
    """
    quote_repo = QuoteRepository(session=session)

    # Clamp day 366 (leap year) to 365 to prevent missing-quote errors
    day_number = min(datetime.now(timezone.utc).timetuple().tm_yday, 365)

    quote = await quote_repo.get_by_day_number(day_number=day_number)
    if quote is None:
        raise NotFoundException(entity="Quote", identifier=str(day_number))

    return quote


async def get_random_quote(session: AsyncSession) -> Quote:
    """Retrieves a random active motivational quote from the repository.

    Args:
        session: The active asynchronous database session.

    Returns:
        A randomly selected active `Quote` model instance.

    Raises:
        NotFoundException: If no active quotes exist in the database.
    """
    quote_repo = QuoteRepository(session=session)

    quote = await quote_repo.get_random_quote()
    if quote is None:
        raise NotFoundException(entity="Quote", identifier="random")

    return quote


async def get_batch_quotes(
    start_day: int,
    end_day: int,
    session: AsyncSession,
) -> list[Quote]:
    """Retrieves a sequential batch range of quotes using a single range query.

    Args:
        start_day: Starting day of year (1-365).
        end_day: Ending day of year (1-365).
        session: The active asynchronous database session.

    Returns:
        A list of Quote model instances found within the specified day range.
    """
    quote_repo = QuoteRepository(session=session)
    return await quote_repo.get_by_day_range(start_day=start_day, end_day=end_day)


