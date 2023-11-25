from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.dialects.mysql import ENUM

from cellcom_scraper.domain.entities import ProcessQueueRequestEntity
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.infrastructure.sqlalchemy.database import Base


class ProcessQueueRequest(Base):
    __tablename__ = "process_queue"

    id = Column(BigInteger, primary_key=True)
    aws_id = Column(BigInteger, nullable=False)
    number_to_port = Column(String(255), nullable=False)
    type = Column(ENUM("PORT IN NUMBER", "SIM EXTRACTION"), nullable=False)
    start_timestamp = Column(DateTime, nullable=False)
    end_timestamp = Column(DateTime, nullable=True)
    status = Column(ENUM("READY", "FINISHED", "ERROR"), nullable=False, default="READY")

    def to_entity(self) -> ProcessQueueRequestEntity:
        return ProcessQueueRequestEntity(
            id=self.id,
            aws_id=self.aws_id,
            number_to_port=self.number_to_port,
            type=RequestType(self.type),
            start_timestamp=self.start_timestamp,
            end_timestamp=self.end_timestamp,
            status=RequestStatus(self.status),
        )
