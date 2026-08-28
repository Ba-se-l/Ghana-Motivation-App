from pydantic import BaseModel as Base, ConfigDict


class QuoteResponse(Base):
    """Single motivational quote."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_number: int
    content: str
    author: str | None
    category: str | None