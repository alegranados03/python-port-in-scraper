import logging

from mediatr import Mediator
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select

from cellcom_scraper.application.queries.get_fictive_number_config import (
    GetFictiveNumberPortIn,
)
from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.domain.entities.process_queue_request import (
    FictiveNumberPortInEntity,
)
from cellcom_scraper.domain.exceptions import (
    PortInNumberException,
    UnknownFictiveNumberPortInException,
)
from cellcom_scraper.config import PORT_IN_AWS_SERVER


class PortInViaFicticeNumberStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials) -> None:
        super().__init__(credentials)
        self.response_server_url = PORT_IN_AWS_SERVER

    def port_in_number(self, configuration: FictiveNumberPortInEntity) -> None:
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
            mobile_phone_input.send_keys(configuration.fictive_number)

            next_step_button = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            next_step_button.click()

            try:
                error_message = self.wait10.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[1]",
                        )
                    )
                )
            except:
                error_message = None

            if error_message is not None:
                raise PortInNumberException(error_message.text)

            select_transaction_dropdown = Select(
                self.wait30.until(
                    ec.presence_of_element_located(
                        (By.XPATH, "//select[@id='transactionTypeProfile']")
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

            number_to_port_input.send_keys(configuration.number_to_port)

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

            current_billing_provider_dropdown = Select(
                self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[4]/div[2]/select[1]",
                        )
                    )
                )
            )
            current_billing_provider_dropdown.select_by_value(
                configuration.current_billing_provider_value
            )

            account_number_input = self.wait10.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//input[@id='accountNumber']")
                )
            )

            account_number_input.send_keys(
                configuration.current_provider_account_number
            )

            customer_authorization = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[10]/div[2]/input[1]",
                    )
                )
            )
            customer_authorization.click()

            customer_name_input = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[11]/div[2]/input[1]",
                    )
                )
            )

            customer_name_input.send_keys(configuration.client_authorization_name)

            quick_submit_button = self.wait10.until(
                ec.presence_of_element_located((By.XPATH, "//button[@id='fSubmitBtn']"))
            )

            quick_submit_button.click()

        except Exception as e:
            message = "Failed during fictice number port in strategy"
            logging.error(e)
            logging.error(message)
            raise e

    def execute(self):
        query: GetFictiveNumberPortIn = GetFictiveNumberPortIn(
            phone_number=self.phone_number
        )
        configuration: FictiveNumberPortInEntity = Mediator.send(query)
        if not configuration:
            message = f"The number {self.phone_number} doesn't have a known configuration in the system"
            raise UnknownFictiveNumberPortInException(message=message)
        self.port_in_number(configuration)

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
