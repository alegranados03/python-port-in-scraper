import logging
import os
from datetime import datetime
from typing import List, Optional

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import (
    AccountEntity,
    ProcessQueueRequestEntity,
    ScraperEntity,
)
from cellcom_scraper.domain.entities.process_queue_request import (
    ProcessQueueUpdateEntity,
)
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.domain.interfaces.uow import UnitOfWork


class Processor:
    def __init__(
        self,
        uow: UnitOfWork,
        controller: Controller,
        account_credentials: AccountEntity,
    ):
        self.uow: UnitOfWork = uow
        self.controller = controller
        self.builder = None
        self.scraper_requests: Optional[List[ProcessQueueRequestEntity]] = None
        self.account_credentials: AccountEntity = account_credentials

    def set_requests(self, requests: List[ProcessQueueRequestEntity]):
        self.scraper_requests = requests

    @staticmethod
    def _get_navigator() -> NavigatorWebDriverType:
        return NavigatorWebDriverType.CHROME

    def _get_account_credentials(self):
        return self.account_credentials

    @staticmethod
    def _get_scraper():
        return ScraperEntity(
            url=os.environ.get("FAST_ACT_URL"),
            slug="port_in_scraper",
            name="Port In Scraper",
        )

    def _update_request_status(self, *, request, status):
        with self.uow:
            repository = self.uow.get_repository("process_requests")
            end_date = datetime.now()
            update_data = ProcessQueueUpdateEntity(
                status=status, end_timestamp=end_date.strftime("%Y-%m-%d %H:%M:%S")
            )
            repository.update(request.id, update_data)
            self.uow.commit()

    def start_processor(self):
        if len(self.scraper_requests) == 0:
            message = "No requests for this execution"
            # logging.info(message)
            print(message)
            return
        for request in self.scraper_requests:
            try:
                request_type = RequestType(request.type)
                credentials: AccountEntity = self._get_account_credentials()
                navigator: NavigatorWebDriverType = self._get_navigator()
                scraper = self._get_scraper()
                self.builder: AutomationDriverBuilder = get_webdriver_builder(
                    navigator
                )(scraper.url)
                self.controller.set_credentials(credentials)
                self.controller.set_strategy(request_type)
                self.controller.set_automation_driver_builder(self.builder)
                self.controller.set_phone_number(request.number_to_port)
                self.controller.set_aws_id(request.aws_id)
                self.controller.execute({})
                self._update_request_status(
                    request=request, status=RequestStatus.FINISHED
                )

            except Exception as error:
                message = (
                    f"Please check request id: {request.id} strategy: {request.type}"
                )
                logging.error(message)
                logging.error(error)
                self._update_request_status(request=request, status=RequestStatus.ERROR)
