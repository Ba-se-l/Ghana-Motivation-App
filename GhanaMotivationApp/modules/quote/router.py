"""Quote domain router."""

from fastapi import APIRouter, Depends, status
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
)
async def get_today_quote(
    session: AsyncSession = Depends(get_session),
) -> QuoteResponse:
    """Returns the quote for today's day-of-year."""
    quote = await service.get_today_quote(session=session)
    return QuoteResponse.model_validate(quote)


@router.get(
    "/random",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a random motivational quote",
)
async def get_random_quote(
    session: AsyncSession = Depends(get_session),
) -> QuoteResponse:
    """Returns a random active motivational quote."""
    quote = await service.get_random_quote(session=session)
    return QuoteResponse.model_validate(quote)