from abc import ABC, abstractmethod
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver


class AutomationDriverBuilder(ABC):
    driver: Optional[WebDriver] = None

    @abstractmethod
    def set_url(self, url):
        raise NotImplementedError

    @abstractmethod
    def set_driver_options(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def initialize_driver(self):
        raise NotImplementedError

    def get_driver(self) -> WebDriver:
        if self.driver:
            return self.driver
