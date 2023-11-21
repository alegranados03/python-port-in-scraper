from typing import Any, Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from cellcom_scraper.domain.entities import AccountEntity

from cellcom_scraper.domain.interfaces.strategy import Strategy


class BaseScraperStrategy(Strategy):
    def __init__(self, credentials: Optional[AccountEntity] = None):
        self.credentials: AccountEntity = credentials
        self.driver: Optional[WebDriver] = None
        self.extras: Optional[dict] = None
        self.wait120: Optional[WebDriverWait] = None
        # TODO: Implement adapters and handle_results to send them to other systems
        self.results: Any = None
        self.request_adapter: Any = None

    def set_credentials(self, credentials: AccountEntity):
        self.credentials = credentials

    def set_driver(self, driver: WebDriver):
        self.driver = driver
        self.wait120 = WebDriverWait(self.driver, 120)

    def set_extras(self, extras: dict):
        self.extras = extras

    def login(self):
        raise NotImplementedError

    def execute(self):
        self.login()

    def handle_results(self):
        raise NotImplementedError
