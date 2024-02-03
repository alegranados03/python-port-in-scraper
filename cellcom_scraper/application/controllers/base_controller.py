from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from cellcom_scraper.application.selectors import get_scraper_strategy

from cellcom_scraper.domain.entities import AccountEntity
from cellcom_scraper.domain.enums import RequestType

from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.domain.interfaces.strategy import Strategy


class BaseController(Controller):
    def __init__(self) -> None:
        self.builder: Optional[AutomationDriverBuilder] = None
        self.strategy: Optional[Strategy] = None
        self.driver: Optional[WebDriver] = None
        self.credentials: Optional[AccountEntity] = None
        self.phone_number: Optional[str] = None
        self.aws_id: Optional[int] = None

    def set_automation_driver_builder(self, builder: AutomationDriverBuilder) -> None:
        self.builder = builder

    def set_strategy(self, scraper_name: RequestType) -> None:
        self.strategy = get_scraper_strategy(scraper_name)(self.credentials)

    def set_credentials(self, credentials: AccountEntity) -> None:
        self.credentials = credentials

    def set_phone_number(self, phone_number: str) -> None:
        self.phone_number = phone_number

    def set_aws_id(self, aws_id: int) -> None:
        self.aws_id = aws_id

    def handle_results(self):
        self.strategy.handle_results(self.aws_id)

    def execute(self, navigator_options: dict):
        raise NotImplementedError
