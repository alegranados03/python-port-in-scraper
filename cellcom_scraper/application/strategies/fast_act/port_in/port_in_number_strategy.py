import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.config import PORT_IN_AWS_SERVER
from cellcom_scraper.domain.exceptions import (
    NoItemFoundException,
    PortInNumberException,
)


class PortInNumberStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = PORT_IN_AWS_SERVER

    def port_in_number(self):
        try:
            logging.info(f"{self.__class__.__name__}: Starting port in process for phone {self.phone_number}")
            portin_dates_changes = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(),'Port-In Date Changes')]")
                )
            )
            logging.debug(f"{self.__class__.__name__}: Port-In Date Changes element found")
            portin_dates_changes.click()
            logging.debug(f"{self.__class__.__name__}: Port-In Date Changes clicked")

            manual_entry = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//a[contains(text(),'Manual Entry')]")
                )
            )
            logging.debug(f"{self.__class__.__name__}: Manual Entry link found")
            manual_entry.click()
            logging.debug(f"{self.__class__.__name__}: Manual Entry clicked")

            portin_number = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//tbody/tr[@id='rowId_0']/td[1]/input[1]")
                )
            )
            logging.debug(f"{self.__class__.__name__}: Port-in number input field found")
            portin_number.send_keys(self.phone_number)
            logging.debug(f"{self.__class__.__name__}: Phone number entered: {self.phone_number}")

            asap_checkbox = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//tbody/tr[@id='rowId_0']/td[6]/input[1]")
                )
            )
            logging.debug(f"{self.__class__.__name__}: ASAP checkbox found")
            asap_checkbox.click()
            logging.debug(f"{self.__class__.__name__}: ASAP checkbox clicked")

            validate_btn = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//a[@id='validate']"))
            )
            logging.debug(f"{self.__class__.__name__}: Validate button found")
            validate_btn.click()
            logging.info(f"{self.__class__.__name__}: Validate clicked, checking for errors")

            rows = self.driver.find_elements(
                By.CSS_SELECTOR, "table > tbody tr[id*=rowId_]"
            )
            logging.debug(f"{self.__class__.__name__}: Found {len(rows)} rows to validate")

            error_number_indexes = []
            for i, row in enumerate(rows):
                if row.get_attribute("style") == "color: rgb(255, 0, 0);":
                    error_number_indexes.append(i)
                    logging.warning(f"{self.__class__.__name__}: Error found at row {i}")

            if len(error_number_indexes) > 0:
                error_msg = self.driver.find_element(
                    By.XPATH,
                    "//body/div[@id='instant_activation']/div[2]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
                )
                logging.error(f"{self.__class__.__name__}: Port-in error: {error_msg.text}")
                raise PortInNumberException(error_msg.text)

            else:
                submit_btn = self.wait30.until(
                    ec.presence_of_element_located((By.XPATH, "//a[@id='submitted']"))
                )
                logging.debug(f"{self.__class__.__name__}: Submit button found")
                submit_btn.click()
                logging.info(f"{self.__class__.__name__}: Port-in submitted successfully")
        except (NoSuchElementException, TimeoutException) as e:
            message = "Failed during port in strategy"
            logging.error(e)
            logging.error(message)
            raise NoItemFoundException(message)

    def execute(self):
        self.port_in_number()

    def handle_results(self):
        screenshot = self.take_screenshot()
        data = {
            "response": "Finished successfully",
            "error_filename": screenshot["filename"],
            "error_screenshot": screenshot["screenshot"],
            "process_id": self.aws_id,
        }
        endpoint: str = "reply-results"
        self.send_to_aws(data, endpoint)

    def handle_errors(
        self, *, error_description, send_sms, send_client_sms="no", error_log=""
    ):
        screenshot: dict = self.take_screenshot()
        data: dict = {
            "error_description": error_description,
            "error_log": error_log,
            "result": "Fail",
            "process_id": self.aws_id,
            "error_filename": screenshot["filename"],
            "error_screenshot": screenshot["screenshot"],
            "send_sms": send_sms,
            "send_client_sms": send_client_sms,
        }
        endpoint: str = "report-errors"
        self.send_to_aws(data, endpoint)
