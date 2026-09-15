"""Quote database seeding utility.

Populates the quotes table with 365 placeholder motivational quotes.
Run this script once after database initialization to ensure
/quotes/today never returns 404 on a fresh database.

Usage:
    python scripts/seed_quotes.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from GhanaMotivationApp.database.session import AsyncSessionLocal
from GhanaMotivationApp.modules.quote.model import Quote


SAMPLE_QUOTES: list[tuple[str, str]] = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("What lies behind us and what lies before us are tiny matters compared to what lies within us.", "Ralph Waldo Emerson"),
]


async def seed_quotes() -> None:
    """Seeds the database with 365 motivational quotes."""
    async with AsyncSessionLocal() as session:
        for day in range(1, 366):
            idx = (day - 1) % len(SAMPLE_QUOTES)
            content, author = SAMPLE_QUOTES[idx]

            stmt = select(Quote).where(Quote.day_number == day)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing is None:
                quote = Quote(
                    day_number=day,
                    content=f"Day {day}: {content}",
                    author=author,
                    category="motivation",
                    is_active=True,
                )
                session.add(quote)

        await session.commit()
        print("Seeded 365 quotes successfully.")


if __name__ == "__main__":
    asyncio.run(seed_quotes())
