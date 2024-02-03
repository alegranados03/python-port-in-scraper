from mediatr import Mediator

from cellcom_scraper.application.queries.get_fictive_number_config import (
    GetFictiveNumberPortIn,
)
from cellcom_scraper.application.strategies.fast_act.port_in.sim_extraction_strategy import (
    SimExtractionStrategy,
)
from cellcom_scraper.domain.entities.process_queue_request import (
    FictiveNumberPortInEntity,
)
from cellcom_scraper.domain.exceptions import UnknownFictiveNumberPortInException


class SimExtractionFictiveNumberStrategy(SimExtractionStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)

    def execute(self):
        query: GetFictiveNumberPortIn = GetFictiveNumberPortIn(
            phone_number=self.phone_number
        )
        configuration: FictiveNumberPortInEntity = Mediator.send(query)
        if not configuration:
            message = f"The number {self.phone_number} doesn't have a known configuration in the system"
            raise UnknownFictiveNumberPortInException(message=message)
        self.set_phone_number(configuration.fictive_number)
        super().execute()
