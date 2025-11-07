import logging

from mediatr import Mediator
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select

from cellcom_scraper.application.queries.get_fictive_number_config import (
    GetFictiveNumberPortIn,
)
from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.config import PORT_IN_AWS_SERVER
from cellcom_scraper.domain.entities.process_queue_request import (
    FictiveNumberPortInEntity,
)
from cellcom_scraper.domain.exceptions import (
    PortInNumberException,
    NoItemFoundException,
    UnknownFictiveNumberPortInException,
)
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception


class PortInViaFicticeNumberStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials) -> None:
        super().__init__(credentials)
        self.response_server_url = PORT_IN_AWS_SERVER

    def port_in_number(self, configuration: FictiveNumberPortInEntity) -> None:
        try:
            logging.info(f"{self.__class__.__name__}: Starting port in process via fictive number: {configuration.fictive_number}")
            portin_dates_changes = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[2]/a[1]",
                    )
                )
            )
            logging.debug(f"{self.__class__.__name__}: Port-in dates changes link found")
            portin_dates_changes.click()
            logging.debug(f"{self.__class__.__name__}: Port-in dates changes clicked")

            mobile_phone_input = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='currentMin']"))
            )
            logging.debug(f"{self.__class__.__name__}: Mobile phone input field found")
            mobile_phone_input.send_keys(configuration.fictive_number)
            logging.debug(f"{self.__class__.__name__}: Fictive number entered: {configuration.fictive_number}")

            next_step_button = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            logging.debug(f"{self.__class__.__name__}: Next step button found")
            next_step_button.click()
            logging.debug(f"{self.__class__.__name__}: Next step clicked")

            try:
                error_message = self.wait10.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[1]",
                        )
                    )
                )
                logging.warning(f"{self.__class__.__name__}: Error message found during fictive number port-in: {error_message.text}")
            except:
                error_message = None

            if error_message is not None:
                raise PortInNumberException(error_message.text)

            logging.debug(f"{self.__class__.__name__}: No error after fictive number entry")

            select_transaction_dropdown = Select(
                self.wait30.until(
                    ec.presence_of_element_located(
                        (By.XPATH, "//select[@id='transactionTypeProfile']")
                    )
                )
            )
            logging.debug(f"{self.__class__.__name__}: Transaction type dropdown found")
            select_transaction_dropdown.select_by_value("CM")
            logging.debug(f"{self.__class__.__name__}: Transaction type 'CM' selected")

            next_step_button2 = self.driver.find_element(
                By.XPATH, "//a[@id='nextButton']"
            )
            logging.debug(f"{self.__class__.__name__}: Next button found")
            next_step_button2.click()
            logging.debug(f"{self.__class__.__name__}: Next button clicked")

            phone_radio_button = self.wait10.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='portRadio']"))
            )
            logging.debug(f"{self.__class__.__name__}: Phone radio button found")
            phone_radio_button.click()
            logging.debug(f"{self.__class__.__name__}: Phone radio button clicked")

            number_to_port_input = self.wait30.until(
                ec.presence_of_element_located(
                    (By.XPATH, "//input[@id='numberToPort']")
                )
            )
            logging.debug(f"{self.__class__.__name__}: Number to port input field found")

            number_to_port_input.send_keys(configuration.number_to_port)
            logging.debug(f"{self.__class__.__name__}: Number to port entered: {configuration.number_to_port}")
            import time
            time.sleep(6)

            # Try multiple paths for the check elegibility button
            check_elegibility_paths = [
                "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[3]/div[4]/div[1]/div[1]/div[1]/button[1]",
                "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[4]/div/div[3]/div[4]/div/div/div[1]/button",
                '//*[@id="portEligibilitySection"]/div[4]/div/div/div[1]/button'
            ]
            button_found = False
            for elegibility_path in check_elegibility_paths:
                try:
                    check_elegibility_button = self.wait30.until(
                        ec.presence_of_element_located(
                            (
                                By.XPATH,
                                elegibility_path,
                            )
                        )
                    )
                    check_elegibility_button.click()
                    logging.info(f"{self.__class__.__name__}: Check eligibility button clicked successfully")
                    button_found = True
                    break
                except Exception as e:
                    message = handle_general_exception(
                        e, f"Exception trying to find elegibility button: {elegibility_path}"
                    )
                    logging.debug(message)
                    print(f"Exception trying to find elegibility button: {elegibility_path}")

            if not button_found:
                logging.error(f"{self.__class__.__name__}: No elegibility button found after trying all paths")
                raise NoItemFoundException(message="check elegibility button not found")

            try:
                error_message = self.wait10.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
                        )
                    )
                )
                logging.warning(f"{self.__class__.__name__}: Port-in eligibility error: {error_message.text}")
            except:
                error_message = None

            if error_message is not None:
                logging.error(f"{self.__class__.__name__}: Port-in rejected due to eligibility: {error_message.text}")
                raise PortInNumberException(error_message.text)

            logging.info(f"{self.__class__.__name__}: Port-in eligibility check passed")

            try:
                # Try multiple paths for billing provider dropdown
                billing_provider_paths = [
                    "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[4]/div[2]/select[1]",
                    "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[4]/div/div[4]/div/div[4]/div[2]/select",
                    '//*[@id="fCurrentBillingProvider"]/div[2]/select'
                ]
                current_billing_provider_dropdown = None
                for provider_path in billing_provider_paths:
                    try:
                        current_billing_provider_dropdown = Select(
                            self.wait30.until(
                                ec.presence_of_element_located(
                                    (By.XPATH, provider_path)
                                )
                            )
                        )
                        logging.debug(f"{self.__class__.__name__}: Billing provider dropdown found")
                        break
                    except Exception as e:
                        message = handle_general_exception(
                            e, f"Exception trying to find billing provider dropdown: {provider_path}"
                        )
                        logging.debug(message)
                        print(f"Exception trying to find billing provider dropdown: {provider_path}")

                if current_billing_provider_dropdown is None:
                    raise NoItemFoundException(message="Billing provider dropdown not found")

                current_billing_provider_dropdown.select_by_value(
                    configuration.current_billing_provider_value
                )
                logging.debug(f"{self.__class__.__name__}: Billing provider selected")

                # Try multiple paths for account number input
                account_number_paths = [
                    "//input[@id='accountNumber']",
                    "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[4]/div/div[4]/div/div[6]/div[2]/input",
                ]
                account_number_input = None
                for account_path in account_number_paths:
                    try:
                        account_number_input = self.wait10.until(
                            ec.presence_of_element_located(
                                (By.XPATH, account_path)
                            )
                        )
                        logging.debug(f"{self.__class__.__name__}: Account number input found")
                        break
                    except Exception as e:
                        message = handle_general_exception(
                            e, f"Exception trying to find account number input: {account_path}"
                        )
                        logging.debug(message)
                        print(f"Exception trying to find account number input: {account_path}")

                if account_number_input is None:
                    raise NoItemFoundException(message="Account number input not found")

                account_number_input.send_keys(
                    configuration.current_provider_account_number
                )
                logging.debug(f"{self.__class__.__name__}: Account number entered")

                # Try multiple paths for customer authorization checkbox
                customer_auth_paths = [
                    "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[10]/div[2]/input[1]",
                    "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[4]/div/div[4]/div/div[10]/div[2]/input",
                    '//*[@id="fCustomerAuthorization"]/div[2]/input'
                ]
                customer_authorization = None
                for auth_path in customer_auth_paths:
                    try:
                        customer_authorization = self.wait10.until(
                            ec.presence_of_element_located(
                                (By.XPATH, auth_path)
                            )
                        )
                        logging.debug(f"{self.__class__.__name__}: Customer authorization checkbox found")
                        break
                    except Exception as e:
                        message = handle_general_exception(
                            e, f"Exception trying to find customer authorization checkbox: {auth_path}"
                        )
                        logging.debug(message)
                        print(f"Exception trying to find customer authorization checkbox: {auth_path}")

                if customer_authorization is None:
                    raise NoItemFoundException(message="Customer authorization checkbox not found")

                customer_authorization.click()
                logging.debug(f"{self.__class__.__name__}: Customer authorization checked")

                # Try multiple paths for customer name input
                customer_name_paths = [
                    "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[4]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[11]/div[2]/input[1]",
                    "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[4]/div/div[4]/div/div[11]/div[2]/input",
                    '//*[@id="fAuthorizationName"]/div[2]/input'
                ]
                customer_name_input = None
                for name_path in customer_name_paths:
                    try:
                        customer_name_input = self.wait10.until(
                            ec.presence_of_element_located(
                                (By.XPATH, name_path)
                            )
                        )
                        logging.debug(f"{self.__class__.__name__}: Customer name input found")
                        break
                    except Exception as e:
                        message = handle_general_exception(
                            e, f"Exception trying to find customer name input: {name_path}"
                        )
                        logging.debug(message)
                        print(f"Exception trying to find customer name input: {name_path}")

                if customer_name_input is None:
                    raise NoItemFoundException(message="Customer name input not found")

                customer_name_input.send_keys(configuration.client_authorization_name)
                logging.debug(f"{self.__class__.__name__}: Customer name entered")

                # Try multiple paths for quick submit button
                quick_submit_paths = [
                    "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[5]/div/div/div[1]/div[2]/button",
                    "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[6]/div/div/div[1]/div[2]/button",
                ]
                quick_submit_button = None
                for submit_path in quick_submit_paths:
                    try:
                        quick_submit_button = self.wait10.until(
                            ec.presence_of_element_located(
                                (By.XPATH, submit_path)
                            )
                        )
                        logging.debug(f"{self.__class__.__name__}: Quick submit button found")
                        break
                    except Exception as e:
                        message = handle_general_exception(
                            e, f"Exception trying to find quick submit button: {submit_path}"
                        )
                        logging.debug(message)
                        print(f"Exception trying to find quick submit button: {submit_path}")

                if quick_submit_button is None:
                    raise NoItemFoundException(message="Quick submit button not found")

                quick_submit_button.click()
                logging.info(f"{self.__class__.__name__}: Quick submit clicked")

                try:
                    step_3_button = self.wait10.until(
                        ec.presence_of_element_located(
                            (By.XPATH,
                             "/html/body/div/div[2]/div/div[2]/div/div[4]/div[1]/div[2]/form/div[14]/div/div/div/button[2]")
                        )
                    )
                    step_3_button.click()
                    logging.debug(f"{self.__class__.__name__}: Step 3 button clicked")

                    step_5_button = self.wait10.until(
                        ec.presence_of_element_located(
                            (By.XPATH,
                             "/html/body/div/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/form/div[4]/button[2]")
                        )
                    )
                    step_5_button.click()
                    logging.debug(f"{self.__class__.__name__}: Step 5 button clicked")
                except Exception as e:
                    logging.warning(f"{self.__class__.__name__}: Optional step buttons not found or couldn't be clicked: {str(e)}")
                    pass
            except (NoSuchElementException, TimeoutException) as e:
                message = "Final port in form not found"
                logging.error(e)
                logging.error(message)
                raise NoItemFoundException(message)

        except (NoSuchElementException, TimeoutException) as e:
            message = "Failed during fictice number port in strategy"
            logging.error(e)
            logging.error(message)
            raise NoItemFoundException(message)

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
