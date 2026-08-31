"""Quote domain HTTP router.

Provides public REST endpoints for retrieving today's motivational quote,
fetching random quotes, and batch-downloading quotes for client offline scheduling.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.database import get_session
from .schema import QuoteResponse
from . import service

router = APIRouter(prefix=f"{settings.API_PREFIX}/quotes", tags=["Quotes"])


@router.get(
    "/today",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get today's motivational quote",
    description="Returns the single motivational quote matching the current UTC day of the year (1-365).",
)
async def get_today_quote(
    session: AsyncSession = Depends(get_session),
) -> QuoteResponse:
    """HTTP endpoint to retrieve today's quote based on day-of-year.

    Args:
        session: Database session dependency injected by FastAPI.

    Returns:
        The `QuoteResponse` schema representing today's quote.
    """
    quote = await service.get_today_quote(session=session)
    return QuoteResponse.model_validate(quote)


@router.get(
    "/random",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a random motivational quote",
    description="Returns a randomly selected active motivational quote.",
)
async def get_random_quote(
    session: AsyncSession = Depends(get_session),
) -> QuoteResponse:
    """HTTP endpoint to retrieve a random motivational quote.

    Args:
        session: Database session dependency injected by FastAPI.

    Returns:
        The `QuoteResponse` schema representing a random quote.
    """
    quote = await service.get_random_quote(session=session)
    return QuoteResponse.model_validate(quote)


@router.get(
    "/batch",
    response_model=list[QuoteResponse],
    status_code=status.HTTP_200_OK,
    summary="Get batch quotes for offline caching",
    description="Returns a list of quotes within a range of day numbers for client-side local notification scheduling.",
)
async def get_batch_quotes(
    start_day: int = Query(..., ge=1, le=365, description="Starting day of year (1-365)"),
    end_day: int = Query(..., ge=1, le=365, description="Ending day of year (1-365)"),
    session: AsyncSession = Depends(get_session),
) -> list[QuoteResponse]:
    """HTTP endpoint to download a batch of quotes for offline client caching.

    Args:
        start_day: Range start integer (1-365).
        end_day: Range end integer (1-365).
        session: Database session dependency injected by FastAPI.

    Returns:
        A list of `QuoteResponse` schemas for the requested day range.
    """
    quotes = await service.get_batch_quotes(
        start_day=start_day,
        end_day=end_day,
        session=session,
    )
    return [QuoteResponse.model_validate(q) for q in quotes]