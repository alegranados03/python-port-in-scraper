from cellcom_scraper.domain.entities import ProcessQueueRequestEntity
from cellcom_scraper.infrastructure.sqlalchemy.models import ProcessQueueRequest
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
