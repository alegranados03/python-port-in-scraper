import base64
import logging
import os
import requests
import json
from datetime import datetime
from typing import Any, Optional

import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from cellcom_scraper.config import AWS_SERVER_URL
from cellcom_scraper.domain.entities import AccountEntity
from cellcom_scraper.domain.interfaces.strategy import Strategy


class BaseScraperStrategy(Strategy):
    def __init__(self, credentials: Optional[AccountEntity] = None):
        self.credentials: AccountEntity = credentials
        self.driver: Optional[WebDriver] = None
        self.phone_number: Optional[str] = None
        self.wait10: Optional[WebDriverWait] = None
        self.wait30: Optional[WebDriverWait] = None
        self.wait60: Optional[WebDriverWait] = None
        self.wait120: Optional[WebDriverWait] = None
        self.results: Any = None
        self.request_adapter: Any = None

    def set_credentials(self, credentials: AccountEntity):
        self.credentials = credentials

    def set_driver(self, driver: WebDriver):
        self.driver = driver
        self.wait10 = WebDriverWait(self.driver, 10)
        self.wait30 = WebDriverWait(self.driver, 30)
        self.wait60 = WebDriverWait(self.driver, 60)
        self.wait120 = WebDriverWait(self.driver, 120)

    def set_phone_number(self, phone_number: str):
        self.phone_number = phone_number

    def login(self):
        raise NotImplementedError

    def execute(self):
        self.login()

    def handle_results(self, aws_id: int):
        raise NotImplementedError

    @staticmethod
    def send_to_aws(data: dict, endpoint: str):
        try:
            response = requests.post(
                f"{AWS_SERVER_URL}/{endpoint}", json=data, timeout=20
            )

            if response.status_code == 200:
                logging.info("Request to AWS sent successfully")
            else:
                # Intenta parsear la respuesta como JSON
                error_info = response.json()
                error_message = f"Request to AWS failed with status code {response.status_code}: {error_info}"
                logging.error(error_message)

        except json.JSONDecodeError:
            logging.error(
                f"Request to AWS failed with status code {response.status_code}: {response.text}"
            )

        except requests.RequestException as e:
            logging.error(f"Request to AWS failed: {e}")

    def take_screenshot(self):
        path = os.getcwd()
        dt = datetime.now().strftime("%Y%m%d %H%M%S").split(" ")
        filename = "_".join([dt[0], self.phone_number, dt[1]])
        fullpath = os.path.join(path, "screenshots", filename)
        self.driver.save_screenshot(fullpath + ".png")

        with open(fullpath + ".png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        return {
            "error_screenshot": encoded,
            "error_filename": filename,
            "fullpath": fullpath,
        }
