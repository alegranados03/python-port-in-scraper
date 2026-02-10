import logging
import os
import time
import sys
from datetime import datetime

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.controllers.base_controller import BaseController
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import AccountEntity
from cellcom_scraper.domain.entities.process_queue_request import (
    ProcessQueueUpdateEntity,
)
from cellcom_scraper.domain.enums import RequestType
from cellcom_scraper.domain.exceptions import (
    ApplicationException,
    LoginFailedException,
    CloseButtonNotFoundException,
)
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from selenium.common.exceptions import NoAlertPresentException


class FastActController(BaseController):
    def __init__(self, uow: UnitOfWork):
        super().__init__(uow)
        self.fast_act_url = os.environ.get("FAST_ACT_URL")
        self._initialize_default_credentials()

    def _initialize_default_credentials(self):
        self.default_credentials = AccountEntity(
            username=os.getenv("BELL_FAST_USERNAME"),
            dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
            password=os.getenv("BELL_FAST_PASSWORD"),
        )
        self.credentials = self.default_credentials

    def _get_credentials_by_request_type(self, request_type: RequestType) -> AccountEntity:
        gta_credentials = AccountEntity(
            username=os.getenv("BELL_FAST_USERNAME"),
            dealer_code=os.getenv("GTA_DEALER_CODE"),
            password=os.getenv("BELL_FAST_PASSWORD"),
        )
        ont_credentials = AccountEntity(
            username=os.getenv("BELL_FAST_USERNAME"),
            dealer_code=os.getenv("ONT_DEALER_CODE"),
            password=os.getenv("BELL_FAST_PASSWORD"),
        )
        wpci_credentials = AccountEntity(
            username=os.getenv("BELL_FAST_USERNAME"),
            dealer_code=os.getenv("WPCI_DEALER_CODE"),
            password=os.getenv("BELL_FAST_PASSWORD"),
        )
        credentials_map: dict = {
            RequestType.PORT_IN_NUMBER: self.default_credentials,
            RequestType.SIM_EXTRACTION: self.default_credentials,
            RequestType.FICTIVE_NUMBER_PORT_IN: self.default_credentials,
            RequestType.FICTIVE_NUMBER_SIM_EXTRACTION: self.default_credentials,
            RequestType.GTA_PORT_IN_NUMBER: gta_credentials,
            RequestType.GTA_SIM_EXTRACTION: gta_credentials,
            RequestType.GTA_FICTIVE_PORT_IN: gta_credentials,
            RequestType.GTA_FICTIVE_SIM_EXTRACTION: gta_credentials,
            RequestType.ONT_PORT_IN_NUMBER: ont_credentials,
            RequestType.ONT_SIM_EXTRACTION: ont_credentials,
            RequestType.ONT_FICTIVE_PORT_IN: ont_credentials,
            RequestType.ONT_FICTIVE_SIM_EXTRACTION: ont_credentials,
            RequestType.WPCI_PORT_IN_NUMBER: wpci_credentials,
            RequestType.WPCI_SIM_EXTRACTION: wpci_credentials,
        }
        return credentials_map.get(request_type, self.default_credentials)

    def _get_url_by_request_type(self, request_type: RequestType) -> str:
        return self.fast_act_url

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

    def _update_request_status(self, *, request, status):
        with self.uow:
            repository = self.uow.get_repository("process_requests")
            end_date = datetime.now()
            update_data = ProcessQueueUpdateEntity(
                status=status, end_timestamp=end_date.strftime("%Y-%m-%d %H:%M:%S")
            )
            repository.update(request.id, update_data)
            self.uow.commit()

    def _update_request_status_without_commit(self, *, request, status):
        repository = self.uow.get_repository("process_requests")
        end_date = datetime.now()
        update_data = ProcessQueueUpdateEntity(
            status=status, end_timestamp=end_date.strftime("%Y-%m-%d %H:%M:%S")
        )
        repository.update(request.id, update_data)

    def set_environment(self):
        while not self.webdriver_is_active():
            if self.system_resources_limit_surpassed():
                sys.exit(100)
            navigator: NavigatorWebDriverType = self._get_navigator()
            self.builder: AutomationDriverBuilder = get_webdriver_builder(
                navigator, self.fast_act_url
            )
            self.builder.set_driver_options(options={})
            self.builder.initialize_driver()
            self.set_driver()
            try:
                self.login()
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

            #modal password cannot be empty
            try:
                print("can fail alert")
                alert = self.wait30.until(ec.alert_is_present())
                time.sleep(5)
                alert.accept()
            except (NoAlertPresentException, Exception) as e:
                print("alert failed")
                print(str(e))
                logging.exception("alert detection failed at login")
                pass
        except (NoSuchElementException, TimeoutException, Exception) as e:
            message = "Failed during FastAct login"
            logging.error(e)
            logging.error(message)
            self.driver.close()
            raise LoginFailedException(message)

    def click_screen_close_button(self):
        option_1 = (
            "/html[1]/body[1]/div[1]/div[1]/div[1]/div[3]/div[1]/ul[1]/li[3]/a[1]"
        )
        option_2 = (
            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]"
        )

        close_options = [option_1, option_2]
        close = None
        for option in close_options:
            try:
                close = self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            option,
                        )
                    )
                )
                close.click()

                try:
                    alert = self.wait30.until(ec.alert_is_present())
                    time.sleep(5)
                    alert.accept()
                except NoAlertPresentException:
                    pass
                break
            except (NoSuchElementException, TimeoutException) as e:
                message = f"{option} button not found"
                logging.error(e)
                logging.error(message)

        if not close:
            raise CloseButtonNotFoundException("Finished without close button")
