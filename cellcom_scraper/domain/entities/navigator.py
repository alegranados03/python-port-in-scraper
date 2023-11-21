from pydantic import BaseModel, Field


class NavigatorEntity(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=0, max_length=100)
