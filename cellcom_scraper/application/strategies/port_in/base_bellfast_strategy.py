import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.base_strategy import BaseScraperStrategy
from cellcom_scraper.domain.exceptions import NoItemFoundException


class BellFastActBaseStrategy(BaseScraperStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)

    def login(self):
        try:
            username_field = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='myUser']"))
            )

            dealer_code_field = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='dealercode']"))
            )

            password_field = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='myPassword']"))
            )

            login_button = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//button[@id='myButton']"))
            )

            username_field.send_keys(self.credentials.username)
            dealer_code_field.send_keys(self.credentials.dealer_code)
            password_field.send_keys(self.credentials.password)
            login_button.click()

        except (NoSuchElementException, TimeoutException, Exception) as e:
            message = "Failed during FastAct login"
            logging.error(e)
            logging.error(message)
            raise NoItemFoundException(message)
