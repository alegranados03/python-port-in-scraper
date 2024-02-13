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
from cellcom_scraper.application.controllers.portin_controller import PortInController
from cellcom_scraper.application.controllers.upgrade_and_dro_controller import (
    UpgradeAndDroController,
)
from cellcom_scraper.domain.enums import ScraperControllerType
from cellcom_scraper.domain.exceptions import UnknownControllerException


class Processor:
    def __init__(
        self,
        uow: UnitOfWork,
        account_credentials: AccountEntity,
    ):
        self.uow: UnitOfWork = uow
        self.controller: Optional[Controller] = None
        self.builder = None
        self.scraper_requests: Optional[List[ProcessQueueRequestEntity]] = None
        self.account_credentials: AccountEntity = account_credentials
        self.cache_scrapers: dict = {}
        self.controllers_list = {
            ScraperControllerType.port_in_scraper: PortInController,
            ScraperControllerType.upgrade_and_dro_scraper: UpgradeAndDroController,
        }

    def get_controller(self, scraper_slug: str) -> Controller:
        if scraper_slug in self.controllers_list:
            return self.controllers_list[ScraperControllerType(scraper_slug)]()
        else:
            raise UnknownControllerException(
                f"{scraper_slug} is not registered in the processor"
            )

    def set_requests(self, requests: List[ProcessQueueRequestEntity]):
        self.scraper_requests = requests

    @staticmethod
    def _get_navigator() -> NavigatorWebDriverType:
        return NavigatorWebDriverType.EDGE

    def _get_account_credentials(self):
        return self.account_credentials

    def _get_scraper(self, scraper_id: int) -> ScraperEntity:
        if scraper_id in self.cache_scrapers:
            return self.cache_scrapers[scraper_id]
        with self.uow:
            scraper: ScraperEntity = self.uow.get_repository("scrapers").get(
                id_=scraper_id
            )
            self.cache_scrapers[scraper_id] = scraper
            return scraper

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
                scraper: ScraperEntity = self._get_scraper(request.scraper_id)
                self.controller = self.get_controller(scraper.slug)
                request_type = RequestType(request.type)
                credentials: AccountEntity = self._get_account_credentials()
                navigator: NavigatorWebDriverType = self._get_navigator()
                self.builder: AutomationDriverBuilder = get_webdriver_builder(
                    navigator, scraper.url
                )
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
