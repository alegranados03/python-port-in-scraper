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


class ProcessQueueUpdateEntity(BaseModel):
    status: str
    end_timestamp: str
