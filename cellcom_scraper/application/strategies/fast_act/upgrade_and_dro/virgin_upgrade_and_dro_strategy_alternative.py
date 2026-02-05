import logging
import re
import time
from datetime import datetime
from typing import Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.config import UPGRADE_AND_DRO_AWS_SERVER
from cellcom_scraper.domain.exceptions import UpgradeStatusException, CloseButtonNotFoundException


class VirginUpgradeAndDroStrategyAlternative(BellFastActBaseStrategy):
    """
    Alternative strategy for Virgin Upgrade and DRO using the OLD website structure.
    Based on commit 4aeb867 - the last version before Angular migration.
    Uses traditional HTML XPaths (/html/body/div/...) instead of Angular components.
    """

    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = UPGRADE_AND_DRO_AWS_SERVER
        self.dro: Optional[str] = None
        self.details: Optional[str] = None
        self.upgrade: Optional[str] = None

    def check_upgrade_and_dro_status(self):
        try:
            # Step 1: Click on Hardware Upgrade link
            hardware_upgrade_link = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/a[1]/span[1]",
                    )
                )
            )
            hardware_upgrade_link.click()

            # Step 2: Enter mobile number
            mobile_number_field = self.wait60.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[1]/div[1]/div[5]/div[2]/input[1]",
                    )
                )
            )
            mobile_number_field.send_keys(self.phone_number)

            # Step 3: Click Next Step button
            next_step_button = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            next_step_button.click()

            # Step 4: Check if error alert appears
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

            except (NoSuchElementException, TimeoutException):
                pass  # No error displayed, continue

            # Step 5: Scroll to upgrade section
            section = self.wait10.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[1]",
                    )
                )
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", section)

            # Step 6: Find upgrade status (multiple paths for fallback)
            upgrade_paths = [
                "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[11]/div[2]",
                "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[4]/form[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[10]/div[2]",
                "/html/body/div/div[2]/div/div[1]/div[4]/form/div/div[3]/div[2]/div[1]/div[1]/div/ul/li[11]/div[2]",
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

            # Step 7: Parse upgrade status
            if "Eligible as of" in upgrade_status_text:
                self.upgrade = self.extract_date(upgrade_status_text)
            elif "Eligible" == upgrade_status_text:
                self.upgrade = "Yes"
            else:
                self.upgrade = "No"

            self.dro = "No"
            return

        except (NoSuchElementException, TimeoutException) as e:
            logging.error(str(e))
            self.dro = "No"
            self.upgrade = "No"
            self.details = "FIELD NOT FOUND"

    def execute(self):
        logging.info(f"PHONE NUMBER: {self.phone_number}")
        self.check_upgrade_and_dro_status()
        details = {"upgrade": self.upgrade, "dro": self.dro, "details": self.details}
        logging.info(details)

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
        # English date format
        match = re.search(
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
            text,
        )
        if match:
            date_str = match.group(0)
            return datetime.strptime(date_str, "%B %d, %Y").date().isoformat()

        # French months (added for compatibility)
        french_months = {
            "janvier": "January",
            "février": "February",
            "mars": "March",
            "avril": "April",
            "mai": "May",
            "juin": "June",
            "juillet": "July",
            "août": "August",
            "septembre": "September",
            "octobre": "October",
            "novembre": "November",
            "décembre": "December",
        }

        french_match = re.search(
            r"\b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{1,2},\s+\d{4}\b",
            text,
            re.IGNORECASE,
        )
        if french_match:
            french_date = french_match.group(0)
            for french_month, english_month in french_months.items():
                if french_month in french_date.lower():
                    english_date = french_date.lower().replace(
                        french_month, english_month
                    )
                    parts = english_date.split()
                    parts[0] = parts[0].capitalize()
                    english_date = " ".join(parts)
                    return datetime.strptime(english_date, "%B %d, %Y").date().isoformat()

        return None


    def click_screen_close_button(self):
        option_1 = "/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div/a[1]"
        option_2 = "/html[1]/body[1]/div[1]/div[1]/div[1]/div[3]/div[1]/ul[1]/li[3]/a[1]"
        option_3 = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]"

        close_options = [option_1, option_2, option_3]
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
                return  # Éxito, salir del método
            except (NoSuchElementException, TimeoutException) as e:
                message = f"{option} button not found"
                logging.error(e)
                logging.error(message)
            except Exception as e:
                # Cualquier otra excepción (WebDriverException, StaleElement, etc.)
                logging.error(f"Unexpected error clicking close button: {e}")

        # Si llegamos aquí, ningún XPath funcionó
        logging.error("Close button not found, forced close")
        raise CloseButtonNotFoundException("Finished without close button")

