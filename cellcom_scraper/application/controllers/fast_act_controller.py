import logging
import os
import time
import traceback
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
from cellcom_scraper.domain.entities.process_queue_request import (
    ProcessQueueUpdateEntity,
)
from cellcom_scraper.domain.exceptions import (
    ApplicationException,
    LoginFailedException,
    CloseButtonNotFoundException,
)
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.uow import UnitOfWork


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
            raise LoginFailedException(message)

    def click_screen_close_button(self):
        option_1 = (
            "/html[1]/body[1]/div[1]/div[1]/div[1]/div[3]/div[1]/ul[1]/li[3]/a[1]"
        )
        option_2 = (
            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]"
        )

        close_options = [option_1, option_2]

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
                break
            except (NoSuchElementException, TimeoutException) as e:
                message = f"{option} button not found"
                logging.error(e)
                logging.error(message)

        if not close:
            raise CloseButtonNotFoundException(message)
