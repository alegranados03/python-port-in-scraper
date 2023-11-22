from pydantic import BaseModel, Field


class ScraperEntity(BaseModel):
    url: str = Field(..., min_length=0, max_length=100)
    slug: str = Field(..., min_length=0, max_length=100)
    name: str = Field(..., min_length=0, max_length=100)
