from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from cellcom_scraper.application.selectors import get_scraper_strategy
from cellcom_scraper.domain.entities import AccountEntity
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.scraper import Scraper
from cellcom_scraper.domain.interfaces.strategy import Strategy


class ScraperController(Scraper):
    def __init__(self):
        self.builder: Optional[AutomationDriverBuilder] = None
        self.strategy: Optional[Strategy] = None
        self.driver: Optional[WebDriver] = None
        self.credentials: Optional[AccountEntity] = None

    def set_automation_driver_builder(self, builder: AutomationDriverBuilder):
        self.builder = builder

    def set_strategy(self, scraper_name: str):
        self.strategy = get_scraper_strategy(scraper_name.lower())(self.credentials)

    def set_credentials(self, credentials: AccountEntity):
        self.credentials = credentials

    def execute(self, navigator_options=None):
        self.builder.set_driver_options(options=navigator_options)
        self.builder.initialize_driver()
        self.strategy.set_driver(self.builder.get_driver())
        self.strategy.execute()

    def handle_results(self):
        self.strategy.handle_results()
