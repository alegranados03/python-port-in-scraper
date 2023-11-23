from abc import ABC, abstractmethod

from selenium.webdriver.remote.webdriver import WebDriver

from cellcom_scraper.domain.entities import AccountEntity


class Strategy(ABC):
    @abstractmethod
    def set_credentials(self, credentials: AccountEntity):
        raise NotImplementedError

    @abstractmethod
    def set_driver(self, driver: WebDriver):
        raise NotImplementedError

    def set_phone_number(self, phone_number: str):
        raise NotImplementedError

    @abstractmethod
    def login(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    def handle_results(self):
        raise NotImplementedError
