from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.dialects.mysql import ENUM

from cellcom_scraper.domain.entities import (
    FictiveNumberPortInEntity,
    ProcessQueueRequestEntity,
)
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.infrastructure.sqlalchemy.database import Base


class ProcessQueueRequest(Base):
    __tablename__ = "process_queue"

    id = Column(BigInteger, primary_key=True)
    aws_id = Column(BigInteger, nullable=False)
    number_to_port = Column(String(255), nullable=False)
    type = Column(
        ENUM(*[e.value for e in RequestType]),
        nullable=False,
    )
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


class FictiveNumberPortIn(Base):
    __tablename__ = "fictive_number_port_in"
    id = Column(BigInteger, primary_key=True)
    number_to_port = Column(String(255), nullable=False)
    fictive_number = Column(String(255), nullable=True)
    current_provider_account_number = Column(String(255), nullable=True)
    client_authorization_name = Column(String(255), nullable=True)
    current_billing_provider_value = Column(
        String(50), comment="this value is for the dropdown in the ui", nullable=True
    )

    def to_entity(self) -> FictiveNumberPortInEntity:
        return FictiveNumberPortInEntity(
            id=self.id,
            number_to_port=self.number_to_port,
            fictive_number=self.fictive_number,
            current_provider_account_number=self.current_provider_account_number,
            client_authorization_name=self.client_authorization_name,
            current_billing_provider_value=self.current_billing_provider_value,
        )
