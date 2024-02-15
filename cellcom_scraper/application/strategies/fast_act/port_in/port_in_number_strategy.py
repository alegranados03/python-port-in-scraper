import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.domain.exceptions import (
    NoItemFoundException,
    PortInNumberException,
)
from cellcom_scraper.config import PORT_IN_AWS_SERVER


class PortInNumberStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = PORT_IN_AWS_SERVER

    def port_in_number(self):
        try:
            portin_dates_changes = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(),'Port-In Date Changes')]")
                )
            )
            portin_dates_changes.click()

            manual_entry = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//a[contains(text(),'Manual Entry')]")
                )
            )
            manual_entry.click()

            portin_number = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//tbody/tr[@id='rowId_0']/td[1]/input[1]")
                )
            )
            portin_number.send_keys(self.phone_number)

            asap_checkbox = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//tbody/tr[@id='rowId_0']/td[6]/input[1]")
                )
            )
            asap_checkbox.click()

            validate_btn = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//a[@id='validate']"))
            )
            validate_btn.click()

            rows = self.driver.find_elements(
                By.CSS_SELECTOR, "table > tbody tr[id*=rowId_]"
            )

            error_number_indexes = []
            for i, row in enumerate(rows):
                if row.get_attribute("style") == "color: rgb(255, 0, 0);":
                    error_number_indexes.append(i)

            if len(error_number_indexes) > 0:
                error_msg = self.driver.find_element(
                    By.XPATH,
                    "//body/div[@id='instant_activation']/div[2]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
                )
                self.handle_errors(error_description=error_msg.text, send_client_sms="yes", send_sms="yes")
                #raise PortInNumberException(error_msg.text)


            else:
                submit_btn = self.wait30.until(
                    ec.presence_of_element_located((By.XPATH, "//a[@id='submitted']"))
                )
                submit_btn.click()
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
