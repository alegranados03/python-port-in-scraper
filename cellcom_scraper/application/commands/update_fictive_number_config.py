from dependency_injector.wiring import Provide, inject
from mediatr import Mediator

from cellcom_scraper.domain.entities.cqrs import Command, CommandHandler
from cellcom_scraper.domain.entities.process_queue_request import (
    FictiveNumberPortInEntity,
)
from cellcom_scraper.infrastructure.injection.containers import (
    PortInRepositoriesContainer,
)
from cellcom_scraper.infrastructure.sqlalchemy.uow import UnitOfWork


class UpdateFictiveNumberPortIn(Command):
    phone_number: str


@Mediator.handler
class UpdateFictiveNumberPortInHandler(CommandHandler[UpdateFictiveNumberPortIn]):
    @inject
    def __init__(
        self,
        uow: UnitOfWork = Provide[PortInRepositoriesContainer.default_uow],
    ) -> None:
        self.uow: UnitOfWork = uow

    def handle(self, command: UpdateFictiveNumberPortIn) -> None:
        pass
