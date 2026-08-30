"""Quote domain service layer."""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from GhanaMotivationApp.core import NotFoundException
from .repo import QuoteRepository
from .model import Quote


async def get_today_quote(session: AsyncSession) -> Quote:
    """Retrieves the motivational quote for today based on day-of-year."""
    quote_repo = QuoteRepository(session=session)
    day_number = datetime.now(timezone.utc).timetuple().tm_yday

    quote = await quote_repo.get_by_day_number(day_number=day_number)
    if quote is None:
        raise NotFoundException(entity="Quote", identifier=str(day_number))
    return quote


async def get_random_quote(session: AsyncSession) -> Quote:
    """Retrieves a random active motivational quote."""
    quote_repo = QuoteRepository(session=session)
    quote = await quote_repo.get_random_quote()
    if quote is None:
        raise NotFoundException(entity="Quote", identifier="random")
    return quote