import logging
import re
from datetime import datetime
from typing import Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.config import UPGRADE_AND_DRO_AWS_SERVER
from cellcom_scraper.domain.exceptions import NoItemFoundException, UpgradeStatusException


class VirginUpgradeAndDroStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = UPGRADE_AND_DRO_AWS_SERVER
        self.dro: Optional[str] = None
        self.details: Optional[str] = None
        self.upgrade: Optional[str] = None

    def check_upgrade_and_dro_status(self):
        try:
            hardware_upgrade_link = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]/span[1]",
                    )
                )
            )

            hardware_upgrade_link.click()

            mobile_number_field = self.wait60.until(
                ec.presence_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[1]/div[1]/div[5]/div[2]/input[1]"))
            )
            mobile_number_field.send_keys(self.phone_number)

            next_step_button = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            next_step_button.click()

            # check if alert appears, if appears set upgrade = NO and DRO = NO
            try:
                cant_open_profile_error = self.wait10.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
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
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[1]"
                    )
                )
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", section)

            upgrade_paths = [
                "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[11]/div[2]",
                "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[10]/div[2]"
            ]
            upgrade_status_text: str = ""
            for upgrade_path in upgrade_paths:
                try:
                    upgrade_status = self.wait10.until(
                        ec.presence_of_element_located(
                            (
                                By.XPATH,
                                upgrade_path,
                            )
                        )
                    )
                    upgrade_status_text = upgrade_status.text
                    if not upgrade_status_text:
                        raise Exception
                except Exception:
                    continue

            if not upgrade_status_text:
                raise UpgradeStatusException("Upgrade status field not found")

            if "Eligible as of" in upgrade_status_text:
                self.upgrade = self.extract_date(upgrade_status_text)
            elif "Eligible" == upgrade_status_text:
                self.upgrade = "Yes"
            else:
                self.upgrade = "No"

            self.dro = "No"
            return

        except (NoSuchElementException, TimeoutException) as e:
            self.dro = "No"
            self.upgrade = "No"
            self.details = "FIELD NOT FOUND"

    def execute(self):
        self.check_upgrade_and_dro_status()

    def handle_results(self):
        screenshot = self.take_screenshot()
        data = {
            "screenshot": screenshot["screenshot"],
            "upgrade": self.upgrade,
            "device_return_option": self.dro,
            "details": self.details,
            "description": "system completed the request",
        }
        endpoint: str = f"phones/{self.aws_id}/logs/info"
        self.send_to_aws(data, endpoint)

    def handle_errors(self, *, description: str, details=""):
        screenshot: dict = self.take_screenshot()
        payload = {
            "description": description,
            "screenshot": screenshot["screenshot"],
            "details": details,
        }
        endpoint: str = f"phones/{self.aws_id}/logs/error"
        self.send_to_aws(data=payload, endpoint=endpoint)

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
