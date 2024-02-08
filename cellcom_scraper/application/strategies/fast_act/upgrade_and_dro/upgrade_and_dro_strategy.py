from typing import Optional

import logging
import re
import time
import random
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.domain.exceptions import (
    NoItemFoundException,
)
from cellcom_scraper.config import UPGRADE_AND_DRO_AWS_SERVER


class UpgradeAndDroStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = UPGRADE_AND_DRO_AWS_SERVER
        self.dro: Optional[str] = None
        self.details: Optional[str] = None
        self.upgrade: Optional[str] = None

    def check_upgrade_and_dro_status(self):
        try:
            hardware_upgrade_link = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]",
                    )
                )
            )

            hardware_upgrade_link.click()

            mobile_number_field = self.wait60.until(
                ec.presence_of_element_located((By.XPATH, "//input[@id='currentMin']"))
            )
            mobile_number_field.send_keys(self.phone_number)

            next_step_button = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            next_step_button.click()

            # check if alert appears, if appears set upgrade = NO and DRO = NO
            try:
                cant_open_profile_error = self.wait60.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
                        )
                    )
                )

                self.dro = "No"
                self.upgrade = "No"
                self.details = cant_open_profile_error.text
                return

            except (NoSuchElementException, TimeoutException) as e:
                pass  # No error displayed


            section = self.wait10.until(
                ec.presence_of_element_located((
                    By.XPATH,"//body/div[@id='instant_activation']/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[1]"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", section)

            upgrade_status = self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[11]/div[2]",
                    )
                )
            )

            upgrade_status_text = upgrade_status.text
            if "Eligible as of" in upgrade_status_text:
                self.upgrade = self.extract_date(upgrade_status_text)
            elif "Eligible" == upgrade_status_text:
                self.upgrade = "Yes"

            # check dro
            try:
                device_description_button = self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/div[1]/div[2]/a[1]",
                        )
                    )
                )
                device_description_button.click()
                self.dro = "Yes"
                time.sleep(random.randint(5, 15))
            except Exception as e:
                self.dro = "No"
                return
            
            try:
                device_description = self.wait30.until(
                    ec.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//body/div[@id='instant_activation']/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/div[1]/div[2]/div[1]/li[1]/div[2]",
                        )
                    )
                )
                deferred_amount = self.wait30.until(
                    ec.visibility_of_element_located(
                        (
                            By.XPATH,
                            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/div[1]/div[2]/div[1]/li[2]/div[2]",
                        )
                    )
                )
                due_date = self.wait30.until(
                        ec.visibility_of_element_located(
                            (
                                By.XPATH,
                                "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/div[1]/div[2]/div[1]/li[3]/div[2]",
                            )
                        )
                )

                details = (
                    f"Device description: {device_description.text} \n"
                    f"Deferred amount:{deferred_amount.text} \n"
                    f"Due date:{self.extract_date(due_date.text)}"
                )
            except Exception as e:
                details = "Couldn't obtain exact details"
            self.details = details

        except (NoSuchElementException, TimeoutException) as e:
            message = "Failed during upgrade and DRO strategy"
            logging.error(e)
            logging.error(message)
            raise NoItemFoundException(message)

    def execute(self):
        super().execute()
        self.check_upgrade_and_dro_status()

    def handle_results(self, aws_id: int):
        screenshot = self.take_screenshot()
        data = {
            "screenshot": screenshot["screenshot"],
            "upgrade": self.upgrade,
            "device_return_option": self.dro,
            "details": self.details,
            "description": "system completed the request",
        }
        endpoint: str = f"phones/{aws_id}/logs/info"
        self.send_to_aws(data, endpoint)

    @staticmethod
    def extract_date(text):
        match = re.search(
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
            text,
        )
        if match:
            date_str = match.group(0)
            return datetime.strptime(date_str, "%B %d, %Y").date().isoformat()
        return None
