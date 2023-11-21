import logging
from typing import List, Optional

from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import ProcessQueueRequestEntity
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.domain.interfaces.automation_driver_builder import \
    AutomationDriverBuilder
from cellcom_scraper.domain.interfaces.scraper import Scraper
from cellcom_scraper.domain.interfaces.uow import UnitOfWork


class Processor:
    def __init__(
        self,
        uow: UnitOfWork,
        controller: Scraper,
    ):
        self.uow: UnitOfWork = uow
        self.controller = controller
        self.builder = None
        self.scraper_requests: Optional[List[ProcessQueueRequestEntity]] = None

    def set_requests(self, requests: List[ProcessQueueRequestEntity]):
        self.scraper_requests = requests

    def _get_navigator(self):
        return ""

    def _update_request_status(self, *, request, status):
        with self.uow:
            pass

    def start_processor(self):
        if len(self.scraper_requests) == 0:
            logging.info("No requests for this execution")
            return
        for request in self.scraper_requests:
            try:
                credentials = self._get_account_credentials(request.account_id)
                navigator = self._get_navigator(request.navigator_id)
                self.builder: AutomationDriverBuilder = get_webdriver_builder(
                    navigator.name
                )(scraper.url)
                self.controller.set_credentials(credentials)
                self.controller.set_strategy()
                self.controller.set_automation_driver_builder(self.builder)

                self.controller.execute()
                # TODO: Implement results handling for each strategy (scraper flow)
                self._update_request_status(
                    request=request, status=RequestStatus.FINISHED
                )
            except Exception as error:
                message = f"Please check request id: {request.id}"
                logging.error(message)
                logging.error(error)
                self._update_request_status(request=request, status=RequestStatus.ERROR)
