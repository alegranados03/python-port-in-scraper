from typing import Optional

from dependency_injector.wiring import Provide, inject
from mediatr import Mediator

from cellcom_scraper.domain.entities.cqrs import Query, QueryHandler
from cellcom_scraper.domain.entities.process_queue_request import (
    FictiveNumberPortInEntity,
)
from cellcom_scraper.infrastructure.injection.containers import (
    PortInRepositoriesContainer,
)
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from cellcom_scraper.infrastructure.sqlalchemy.uow import UnitOfWork


class GetFictiveNumberPortIn(Query):
    phone_number: str


@Mediator.handler
class GetFictiveNumberPortInHandler(
    QueryHandler[GetFictiveNumberPortIn, Optional[FictiveNumberPortInEntity]]
):
    @inject
    def __init__(self, uow: UnitOfWork = DefaultUnitOfWork()) -> None:
        self.uow: UnitOfWork = uow

    def handle(
        self, query: GetFictiveNumberPortIn
    ) -> Optional[FictiveNumberPortInEntity]:
        with self.uow:
            repository = self.uow.get_repository("fictive_number_port_in")
            return repository.get_by_filter(number_to_port=query.phone_number)
