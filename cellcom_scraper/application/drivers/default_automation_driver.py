from typing import Callable, Dict, Tuple

from cellcom_scraper.domain.interfaces.automation_driver import AutomationDriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

Locator = Tuple[By, str]


class DefaultAutomationDriver(AutomationDriver):
    def __init__(self, driver: WebDriver):
        self.driver: WebDriver = driver
        self._waits: Dict[int, WebDriverWait] = {}

    def wait_for_element(
        self,
        locator: Locator,
        condition: Callable[[Locator], WebElement],
        seconds: int = 30,
    ):
        wait = self._get_webdriver_wait(seconds)
        return wait.until(condition(locator))

    def _get_webdriver_wait(self, seconds: int):
        if seconds not in self._waits:
            self._waits[seconds] = WebDriverWait(self.driver, seconds)
        return self._waits[seconds]
