from pydantic import BaseModel, Field


class AccountEntity(BaseModel):
    username: str = Field(..., min_length=0, max_length=100)
    dealer_code: str = Field(..., min_length=0, max_length=100)
    password: str = Field(..., min_length=0, max_length=100)
