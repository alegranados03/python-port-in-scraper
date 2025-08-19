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
from cellcom_scraper.domain.exceptions import (
    NoItemFoundException,
    UpgradeStatusException,
)


class VirginUpgradeAndDroStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = UPGRADE_AND_DRO_AWS_SERVER
        self.dro: Optional[str] = None
        self.details: Optional[str] = None
        self.upgrade: Optional[str] = None

    def check_upgrade_and_dro_status(self):
        try:
            search_input = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/form/div[1]/div[1]/div/input",
                    )
                )
            )
            search_input.send_keys(self.phone_number)

            search_button = self.wait60.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/button",
                    )
                )
            )
            search_button.click()

            try:
                modal_selector = self.wait120.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/form/div[1]/div[3]/div/div/div/div/app-fuzzy-match-lightbox/div/div/div/div[2]/div/div[2]/div[1]/label[1]",
                        )
                    )
                )
                modal_selector.click()
                select_option_button = self.wait120.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/form/div[1]/div[3]/div/div/div/div/app-fuzzy-match-lightbox/div/div/div/div[3]/button[1]",
                        )
                    )
                )
                select_option_button.click()
            except NoSuchElementException:
                pass

            try:
                self.wait120.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/form/div[2]",
                        )
                    )
                )
                self.wait120.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[1]",
                        )
                    )
                )
                self.dro = "No"
                self.upgrade = "No"
                self.details = "FIELD NOT FOUND"
            except NoSuchElementException:
                pass # error message no deployed

            try:
                #email request modal, ignore.
                modal_discard = "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/app-customer-services-available/div/div/div[10]/div/div/div[3]/button[2]"
                modal_button = self.wait120.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            modal_discard,
                        )
                    )
                )
                modal_button.click()

            except:
                #didn't appear
                pass


            section = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details",
                    )
                )
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", section)

            upgrade_paths = [
                "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details/div[1]/div/table/tr[3]/td[1]/div/p",
                "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details/div[1]/div/table/tr[2]/td[1]/div/p"
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
                    upgrade_status_text = upgrade_status.text.strip()
                    if upgrade_status_text:
                        break
                except Exception as e:
                    logging.error(str(e))
                    continue

            if not upgrade_status_text:
                raise UpgradeStatusException("Upgrade status field not found")

            if "Eligible as of" in upgrade_status_text or "Admissible à partir du" in upgrade_status_text:
                self.upgrade = self.extract_date(upgrade_status_text)
            elif "Eligible" == upgrade_status_text or "Admissible" == upgrade_status_text:
                self.upgrade = "Yes"
            else:
                self.upgrade = "No"
            #TODO: FINISH DRO
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
