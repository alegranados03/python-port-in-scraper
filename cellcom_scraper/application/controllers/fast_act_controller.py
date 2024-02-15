from cellcom_scraper.config import FORCE_STOP_ERRORS, MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import ApplicationException
from cellcom_scraper.application.controllers.base_controller import BaseController

from cellcom_scraper.domain.interfaces.uow import UnitOfWork

from cellcom_scraper.domain.entities import (
    AccountEntity,
    ProcessQueueRequestEntity,
    ScraperEntity,
)
from cellcom_scraper.domain.entities.process_queue_request import (
    ProcessQueueUpdateEntity,
)
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.application.enums import NavigatorWebDriverType
from datetime import datetime
import os
import logging


class FastActController(BaseController):
    def __init__(self, uow: UnitOfWork):
        super().__init__(uow)
        self.fast_act_url = os.environ.get("FAST_ACT_URL")

    def _get_requests(self) -> None:
        try:
            with self.uow:
                self.requests = self.uow.get_repository("process_requests").filter(
                    status="READY", scraper_id__in=[1, 2]
                )
        except Exception as e:
            message = "Connection could be unavailable, please check database"
            logging.error(message)
            logging.error(e)
            print(message)

    def _update_request_status(self, *, request, status):
        with self.uow:
            repository = self.uow.get_repository("process_requests")
            end_date = datetime.now()
            update_data = ProcessQueueUpdateEntity(
                status=status, end_timestamp=end_date.strftime("%Y-%m-%d %H:%M:%S")
            )
            repository.update(request.id, update_data)
            self.uow.commit()

    def start_environment(self):
        navigator: NavigatorWebDriverType = self._get_navigator()
        self.builder: AutomationDriverBuilder = get_webdriver_builder(
            navigator, self.fast_act_url
        )
        self.builder.set_driver_options(options={})
        self.builder.initialize_driver()
        self.set_driver()
        # here should log in and keep active while it's solving requests
    def execute(self):
        for request in self.requests:
            # try catch for all this
            request_type: RequestType = RequestType(request.type)
            self.set_strategy(request_type)
            self.strategy.set_driver(self.builder.get_driver())
            self.strategy.set_phone_number(request.phone_number)
            self.strategy.execute()
            self.handle_results()
