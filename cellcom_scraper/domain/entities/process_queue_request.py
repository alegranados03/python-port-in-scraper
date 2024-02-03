from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from cellcom_scraper.domain.enums import RequestStatus, RequestType


class ProcessQueueRequestEntity(BaseModel):
    id: Optional[int] = None
    aws_id: int
    number_to_port: str
    type: RequestType
    start_timestamp: datetime
    end_timestamp: Optional[datetime] = None
    status: RequestStatus
    scraper_id: int


class FictiveNumberPortInEntity(BaseModel):
    id: int
    number_to_port: str
    fictive_number: Optional[str] = (None,)
    current_provider_account_number: Optional[str] = (None,)
    client_authorization_name: Optional[str] = (None,)
    current_billing_provider_value: Optional[str] = None


class ProcessQueueUpdateEntity(BaseModel):
    status: str
    end_timestamp: str
