from pydantic import BaseModel, Field
from cellcom_scraper.domain.enums import ExecutionFrequency


class ScraperEntity(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=0, max_length=500)
    url: str = Field(..., min_length=0, max_length=100)
    slug: str = Field(..., min_length=0, max_length=100)
    execution_frequency: ExecutionFrequency = ExecutionFrequency.ONCE
    available: bool = Field(...)
