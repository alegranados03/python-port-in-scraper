import logging
from typing import List, Optional

from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import ProcessQueueRequestEntity
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.scraper import Scraper
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from cellcom_scraper.application.enums import NavigatorWebDriverType, StrategyName
from cellcom_scraper.domain.entities import AccountEntity, ScraperEntity


class Processor:
    def __init__(
        self, uow: UnitOfWork, controller: Scraper, account_credentials: AccountEntity
    ):
        self.uow: UnitOfWork = uow
        self.controller = controller
        self.builder = None
        self.scraper_requests: Optional[List[ProcessQueueRequestEntity]] = None
        self.account_credentials: AccountEntity = account_credentials

    def set_requests(self, requests: List[ProcessQueueRequestEntity]):
        self.scraper_requests = requests

    def _get_navigator(self) -> NavigatorWebDriverType:
        return NavigatorWebDriverType.CHROME

    def _get_account_credentials(self):
        return self.account_credentials

    def _get_scraper(self):
        return ScraperEntity(
            url="https://wac.bell.ca:8000/wac-ia/bell_login.jsp",
            slug="port_in_scraper",
            name="Port In Scraper",
        )

    def _update_request_status(self, *, request, status):
        with self.uow:
            pass
            self.uow.commit()

    def start_processor(self):
        if len(self.scraper_requests) == 0:
            logging.info("No requests for this execution")
            return
        for request in self.scraper_requests:
            try:
                credentials: AccountEntity = self._get_account_credentials()
                navigator: NavigatorWebDriverType = self._get_navigator()
                scraper = self._get_scraper()
                self.builder: AutomationDriverBuilder = get_webdriver_builder(
                    navigator
                )(scraper.url)
                self.controller.set_credentials(credentials)
                self.controller.set_strategy(request.type)
                self.controller.set_automation_driver_builder(self.builder)
                self.controller.execute()
                self._update_request_status(
                    request=request, status=RequestStatus.FINISHED
                )
            except Exception as error:
                message = f"Please check request id: {request.id}"
                logging.error(message)
                logging.error(error)
                self._update_request_status(request=request, status=RequestStatus.ERROR)
