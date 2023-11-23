from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from cellcom_scraper.application.selectors import get_scraper_strategy
from cellcom_scraper.domain.entities import AccountEntity
from cellcom_scraper.domain.enums import RequestType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.scraper import Scraper
from cellcom_scraper.domain.interfaces.strategy import Strategy
from cellcom_scraper.config import MAX_ATTEMPTS, FORCE_STOP_ERRORS


class ScraperController(Scraper):
    def __init__(self):
        self.builder: Optional[AutomationDriverBuilder] = None
        self.strategy: Optional[Strategy] = None
        self.driver: Optional[WebDriver] = None
        self.credentials: Optional[AccountEntity] = None
        self.phone_number: Optional[str] = None

    def set_automation_driver_builder(self, builder: AutomationDriverBuilder):
        self.builder = builder

    def set_strategy(self, scraper_name: RequestType):
        self.strategy = get_scraper_strategy(scraper_name)(self.credentials)

    def set_credentials(self, credentials: AccountEntity):
        self.credentials = credentials

    def set_phone_number(self, phone_number: str):
        self.phone_number = phone_number

    def execute(self, navigator_options=None):
        tries = 0
        while tries < MAX_ATTEMPTS:
            tries += 1
            self.builder.set_driver_options(options=navigator_options)
            self.builder.initialize_driver()
            self.strategy.set_driver(self.builder.get_driver())
            self.strategy.set_phone_number(self.phone_number)
            try:
                self.strategy.execute()
                tries = MAX_ATTEMPTS + 1
            except Exception as e:
                for error in FORCE_STOP_ERRORS:
                    if error in str(e):
                        tries = MAX_ATTEMPTS

                if tries == MAX_ATTEMPTS:
                    print(e)

    def handle_results(self):
        self.strategy.handle_results()
