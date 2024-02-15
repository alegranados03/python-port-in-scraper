from cellcom_scraper.config import FORCE_STOP_ERRORS, MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import ApplicationException
from cellcom_scraper.application.controllers.base_controller import BaseController

from cellcom_scraper.domain.interfaces.uow import UnitOfWork

from cellcom_scraper.domain.entities import (
    AccountEntity,
    ProcessQueueRequestEntity,
    ScraperEntity,
)
from cellcom_scraper.domain.entities.process_queue_request import (
    ProcessQueueUpdateEntity,
)
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.application.enums import NavigatorWebDriverType
from datetime import datetime
from cellcom_scraper.config import FORCE_STOP_ERRORS, MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import ApplicationException
import os
import logging
import traceback
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from cellcom_scraper.domain.exceptions import NoItemFoundException
from selenium.common.exceptions import WebDriverException


class FastActController(BaseController):
    def __init__(self, uow: UnitOfWork):
        super().__init__(uow)
        self.fast_act_url = os.environ.get("FAST_ACT_URL")

    def webdriver_is_active(self):
        if not self.driver:
            return False
        try:
            if self.driver.window_handles:
                return True
            else:
                return False
        except WebDriverException:
            return False

    def _get_requests(self) -> None:
        try:
            with self.uow:
                self.requests = self.uow.get_repository("process_requests").filter(
                    status="READY", scraper_id=1
                )
        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            full_error_message = (
                f"Exception Type:"
                f"{error_type}\n Message: {error_message}\n Traceback:\n{error_traceback}"
            )
            logging.error(full_error_message)

    def _update_request_status(self, *, request, status):
        with self.uow:
            repository = self.uow.get_repository("process_requests")
            end_date = datetime.now()
            update_data = ProcessQueueUpdateEntity(
                status=status, end_timestamp=end_date.strftime("%Y-%m-%d %H:%M:%S")
            )
            repository.update(request.id, update_data)
            self.uow.commit()

    def set_environment(self):
        while not self.webdriver_is_active():
            navigator: NavigatorWebDriverType = self._get_navigator()
            self.builder: AutomationDriverBuilder = get_webdriver_builder(
                navigator, self.fast_act_url
            )
            self.builder.set_driver_options(options={})
            self.builder.initialize_driver()
            self.set_driver()
            try:
                self.login()
                pass
            except ApplicationException as e:
                logging.error(e.message)
                print(e.message)
                pass

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
            time.sleep(5)
            login_button.click()
            time.sleep(10)

        except (NoSuchElementException, TimeoutException, Exception) as e:
            message = "Failed during FastAct login"
            logging.error(e)
            logging.error(message)
            self.driver.close()
            raise NoItemFoundException(message)

    def execute(self):
        self._get_requests()
        for request in self.requests:
            self.set_environment()
            request_type: RequestType = RequestType(request.type)
            self.set_strategy(request_type)
            self.strategy.set_driver(self.builder.get_driver())
            self.strategy.set_phone_number(request.number_to_port)
            self.strategy.set_aws_id(request.aws_id)
            tries = 0
            while tries < MAX_ATTEMPTS:
                try:
                    self.strategy.execute()
                    self.handle_results()
                    tries = MAX_ATTEMPTS + 1
                    self._update_request_status(
                        request=request, status=RequestStatus.FINISHED
                    )
                    if self.webdriver_is_active():
                        try:
                            close = self.wait30.until(
                                ec.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        "/html[1]/body[1]/div[1]/div[1]/div[1]/div[3]/div[1]/ul[1]/li[3]/a[1]",
                                    )
                                )
                            )
                            close.click()
                        except Exception: 
                            close = self.wait30.until(
                            ec.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]",
                                )
                            )
                        )
                        close.click()
                            
                except ApplicationException as e:
                    for error in FORCE_STOP_ERRORS:
                        if error in str(e):
                            tries = MAX_ATTEMPTS
                            break
                    if tries == MAX_ATTEMPTS:
                        self._update_request_status(
                            request=request, status=RequestStatus.ERROR
                        )
                        self.strategy.handle_errors(
                            error_description=e.message,
                            send_sms="yes",
                            send_client_sms="yes",
                        )
                        raise ApplicationException("Scraper request failed", "E001")
                    else:
                        self.strategy.handle_errors(
                            error_description=e.message, send_sms="no"
                        )
                except Exception as e:
                    message = (
                        "Another type of exception occurred please check what happened"
                    )
                    error_message = str(e)
                    error_type = type(e).__name__
                    error_traceback = traceback.format_exc()
                    full_error_message = (
                        f"Exception Type:"
                        f"{error_type}\n Message: {error_message}\n Traceback:\n{error_traceback}"
                    )
                    logging.error(full_error_message)
                    logging.error(message)
                    self.strategy.handle_errors(
                        error_description=message,
                        send_sms="yes",
                        error_log=full_error_message,
                    )
