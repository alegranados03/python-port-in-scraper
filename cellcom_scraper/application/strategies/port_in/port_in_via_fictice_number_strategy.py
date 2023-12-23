from cellcom_scraper.application.strategies.port_in.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from cellcom_scraper.domain.exceptions import (
    NoItemFoundException,
    PortInNumberException,
)
import logging


class PortInViaFicticeNumberStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)

    def port_in_number(self):
        try:
            portin_dates_changes = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[2]/a[1]",
                    )
                )
            )
            portin_dates_changes.click()

            mobile_phone_input = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='currentMin']"))
            )
            mobile_phone_input.send_keys()

            next_step_button = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            next_step_button.click()

            select_transaction_dropdown = Select(
                self.wait30.until(
                    ec.presence_of_element_located(
                        (By.XPATH, "//select[@id='transactionTypeProfile']0")
                    )
                )
            )
            select_transaction_dropdown.select_by_value("CM")

            next_step_button2 = self.driver.find_element(
                By.XPATH, "//a[@id='nextButton']"
            )
            next_step_button2.click()

            phone_radio_button = self.wait10.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='portRadio']"))
            )
            phone_radio_button.click()

            number_to_port_input = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//input[@id='numberToPort']")
                )
            )

            number_to_port_input.send_keys()

            check_elegibility_button = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[3]/div[4]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            check_elegibility_button.click()

            try:
                error_message = self.wait10.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
                        )
                    )
                )
            except:
                error_message = None

            if error_message is not None:
                raise PortInNumberException(error_message.text)

        except Exception as e:
            message = "Failed during port in strategy"
            logging.error(e)
            logging.error(message)
            raise NoItemFoundException(message)

    def execute(self):
        super().execute()

    def handle_results(self, aws_id: int):
        screenshot = self.take_screenshot()
        data = {
            "response": "Finished successfully",
            "error_filename": screenshot["error_filename"],
            "error_screenshot": screenshot["error_screenshot"],
            "process_id": aws_id,
        }
        endpoint: str = "reply-results"
        self.send_to_aws(data, endpoint)
