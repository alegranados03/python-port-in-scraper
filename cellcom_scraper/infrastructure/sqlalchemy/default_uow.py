from sqlalchemy.orm import sessionmaker

from cellcom_scraper.infrastructure.repositories import (
    FictiveNumberPortInRepository,
    ProcessQueueRequestRepository,
)
from cellcom_scraper.infrastructure.sqlalchemy.database import SESSION_FACTORY
from cellcom_scraper.infrastructure.sqlalchemy.uow import SQLAlchemyUnitOfWork


class DefaultUnitOfWork(SQLAlchemyUnitOfWork):
    def __init__(self, session_factory: sessionmaker = SESSION_FACTORY) -> None:
        super(DefaultUnitOfWork, self).__init__(session_factory)

    def __enter__(self) -> "DefaultUnitOfWork":
        super(DefaultUnitOfWork, self).__enter__()
        self.process_requests: ProcessQueueRequestRepository = (
            ProcessQueueRequestRepository(self.session)
        )
        self.fictive_number_port_in: FictiveNumberPortInRepository = (
            FictiveNumberPortInRepository(self.session)
        )
        return self
