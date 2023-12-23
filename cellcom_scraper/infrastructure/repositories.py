from cellcom_scraper.domain.entities import (
    ProcessQueueRequestEntity,
    FictiveNumberPortInEntity,
)
from cellcom_scraper.infrastructure.sqlalchemy.models import (
    ProcessQueueRequest,
    FictiveNumberPortIn,
)
from cellcom_scraper.infrastructure.sqlalchemy.repository import SQLAlchemyRepository


class ProcessQueueRequestRepository(SQLAlchemyRepository):
    class Meta:
        model = ProcessQueueRequest

    def to_orm_model(self, entity: ProcessQueueRequestEntity) -> ProcessQueueRequest:
        return ProcessQueueRequest(
            id=entity.id,
            aws_id=entity.aws_id,
            number_to_port=entity.number_to_port,
            type=entity.type.value,
            start_timestamp=entity.start_timestamp,
            end_timestamp=entity.end_timestamp,
            status=entity.status.value,
        )


class FictiveNumberPortInRepository(SQLAlchemyRepository):
    class Meta:
        model = FictiveNumberPortIn

    def to_orm_model(self, entity: FictiveNumberPortInEntity) -> FictiveNumberPortIn:
        return FictiveNumberPortIn(
            id=entity.id,
            number_to_port=entity.number_to_port,
            fictive_number=entity.fictive_number,
            current_provider_account_number=entity.current_provider_account_number,
            client_authorization_name=entity.client_authorization_name,
            current_billing_provider_value=entity.current_billing_provider_value,
        )
