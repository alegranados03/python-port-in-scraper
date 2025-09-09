import psutil
import logging
import os

from typing import List, Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_scraper_strategy
from cellcom_scraper.domain.entities import (
    AccountEntity,
    ProcessQueueRequestEntity,
    ScraperEntity,
)
from cellcom_scraper.domain.enums import RequestType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.domain.interfaces.strategy import Strategy
from cellcom_scraper.domain.interfaces.uow import UnitOfWork


class BaseController(Controller):
    def __init__(self, uow: UnitOfWork) -> None:
        self.builder: Optional[AutomationDriverBuilder] = None
        self.strategy: Optional[Strategy] = None
        self.driver: Optional[WebDriver] = None
        self.credentials: Optional[AccountEntity] = None
        self.request: Optional[ProcessQueueRequestEntity] = None
        self.cache_scrapers: dict = {}
        self.uow: UnitOfWork = uow
        self.wait30: Optional[WebDriverWait] = None

    def set_automation_driver_builder(self, builder: AutomationDriverBuilder) -> None:
        self.builder = builder

    def set_strategy(self, scraper_name: RequestType) -> None:
        self.strategy = get_scraper_strategy(scraper_name)(
            self._get_account_credentials()
        )

    def set_credentials(self, credentials: AccountEntity) -> None:
        self.credentials = credentials

    def set_driver(self):
        if self.builder:
            self.driver = self.builder.get_driver()
            self.wait30 = WebDriverWait(self.driver, 10)

    def _get_account_credentials(self) -> AccountEntity:
        return self.credentials

    def handle_results(self):
        self.strategy.handle_results()

    def handle_errors(self, **kwargs):
        self.strategy.handle_errors(**kwargs)

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
    def system_resources_limit_surpassed():
        process = psutil.Process(os.getpid())
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = process.memory_info().rss / (1024 * 1024 * 1024)  # GB

        max_cpu_usage = 65  # 65%
        max_memory_usage = (
            0.5 * psutil.virtual_memory().total / (1024 * 1024 * 1024)
        )  # 50% del total de memoria

        if cpu_usage > max_cpu_usage or memory_usage > max_memory_usage:
            logging.error(
                f"Resource limit exceeded. CPU: {cpu_usage}%, Memory: {memory_usage}GB"
            )
            return True
        logging.info(
            f"Current resources usage. CPU: {cpu_usage}%, Memory: {memory_usage}GB"
        )
        return False

    @staticmethod
    def _get_navigator() -> NavigatorWebDriverType:
        return NavigatorWebDriverType.CHROME

    def _get_request(self) -> None:
        raise NotImplementedError

    def _update_request_status(self, *, request, status):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def login(self):
        raise NotImplementedError

    def set_environment(self):
        raise NotImplementedError
