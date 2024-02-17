from typing import Callable, Dict, Tuple

from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

Locator = Tuple[By, str]


class AutomationDriver(ABC):
    @abstractmethod
    def wait_for_element(
        self,
        locator: Locator,
        condition: Callable[[Locator], WebElement],
        seconds: int = 30,
    ):
        pass

    @abstractmethod
    def get_webdriver_wait(self, timeout: int):
        pass
