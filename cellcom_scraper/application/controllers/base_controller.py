from typing import Optional, List

from selenium.webdriver.remote.webdriver import WebDriver

from cellcom_scraper.application.selectors import get_scraper_strategy


from cellcom_scraper.domain.enums import RequestType

from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.domain.interfaces.strategy import Strategy
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from cellcom_scraper.domain.entities import (
    AccountEntity,
    ProcessQueueRequestEntity,
    ScraperEntity,
)
from cellcom_scraper.application.enums import NavigatorWebDriverType


class BaseController(Controller):
    def __init__(self, uow: UnitOfWork) -> None:
        self.builder: Optional[AutomationDriverBuilder] = None
        self.strategy: Optional[Strategy] = None
        self.driver: Optional[WebDriver] = None
        self.credentials: Optional[AccountEntity] = None
        self.requests: Optional[List[ProcessQueueRequestEntity]] = None
        self.cache_scrapers: dict = {}
        self.uow: UnitOfWork = uow

    def set_automation_driver_builder(self, builder: AutomationDriverBuilder) -> None:
        self.builder = builder

    def set_strategy(self, scraper_name: RequestType) -> None:
        self.strategy = get_scraper_strategy(scraper_name)(self._get_account_credentials())

    def set_credentials(self, credentials: AccountEntity) -> None:
        self.credentials = credentials

    def set_driver(self):
        if self.builder:
            self.driver = self.builder.get_driver()

    def _get_account_credentials(self) -> AccountEntity:
        return self.credentials

    def handle_results(self):
        self.strategy.handle_results()

    def handle_errors(self):
        self.strategy.handle_errors()

    def _get_scraper(self, scraper_id: int) -> ScraperEntity:
        if scraper_id in self.cache_scrapers:
            return self.cache_scrapers[scraper_id]
        with self.uow:
            scraper: ScraperEntity = self.uow.get_repository("scrapers").get(
                id_=scraper_id
            )
            self.cache_scrapers[scraper_id] = scraper
            return scraper

    @staticmethod
    def _get_navigator() -> NavigatorWebDriverType:
        return NavigatorWebDriverType.EDGE

    def _get_requests(self) -> None:
        raise NotImplementedError

    def _update_request_status(self, *, request, status):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
