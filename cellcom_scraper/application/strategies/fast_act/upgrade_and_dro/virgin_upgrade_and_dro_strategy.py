import logging
import re
import time
from datetime import datetime
from typing import Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import \
    BellFastActBaseStrategy
from cellcom_scraper.config import UPGRADE_AND_DRO_AWS_SERVER


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

            time.sleep(15)
            try:
                print("looking for no profile warning")
                div_elem = self.wait30.until(
                    ec.presence_of_element_located(
                        (By.XPATH, '//*[@id="customerPage-exc"]/form/div[2]')
                    )
                )

                classes = div_elem.get_attribute("class")
                if "errMsg" in classes:
                    print("❌ error:", div_elem.text)
                else:
                    print("✅ div normal")
                    raise Exception("it exists a profile")
                self.dro = "No"
                self.upgrade = "No"
                self.details = "NO PROFILE DISPLAYED"
                return
            except Exception as e:
                logging.info("profile exists")
                print(str(e))

            try:
                print("checking if modal exists")
                modal_selector = self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/form/div[1]/div[3]/div/div/div/div/app-fuzzy-match-lightbox/div/div/div/div[2]/div/div[2]/div[1]/label[1]",
                        )
                    )
                )
                print("it exists")
                modal_selector.click()
                select_option_button = self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-landing-page/div/div/div[1]/div[2]/div[1]/div[1]/app-existing-customer-search/div/form/div[1]/div[3]/div/div/div/div/app-fuzzy-match-lightbox/div/div/div/div[3]/button[1]",
                        )
                    )
                )
                select_option_button.click()
            except Exception:
                print("no modal or couldn't select option")
                pass

            try:
                # email request modal, ignore.
                print("email request modal to ignore")
                modal_discard = "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/app-customer-services-available/div/div/div[10]/div/div/div[3]/button[2]"
                modal_button = self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            modal_discard,
                        )
                    )
                )
                modal_button.click()

            except:
                logging.warning("no email modal")
                pass

            try:
                print("looking phone section")
                section = self.wait10.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details",
                        )
                    )
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", section
                )
            except:
                print("couldn't scroll down")
                logging.error("couldn't scroll down")

            logging.info("going to upgrade paths")
            print("going to upgrade paths")
            upgrade_paths = [
                "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details/div[1]/div/table/tr[2]/td[1]/div/p",
                "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details/div[1]/div/table/tr[3]/td[1]/div/p",
                "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div[1]/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details/div[1]/div/table/tr[2]/td[1]/div/p",
                "/html[1]/body[1]/app-root[1]/div[1]/div[1]/div[2]/app-customer-homepage[1]/div[1]/div[1]/div[1]/div[3]/div[3]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/app-mobility-device-details[1]/div[1]/div[1]/table[1]/tr[2]/td[1]/div[1]/p[1]",
                "/html/body/app-root/div[1]/div[1]/div[2]/app-customer-homepage/div[1]/div[1]/div/div[3]/div[3]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/app-mobility-device-details/div[1]/div/table/tr[2]/td[1]/div/p",
            ]

            self.upgrade = "No"

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
                    upgrade_status_text = (
                        upgrade_status.text.strip()
                        if upgrade_status is not None
                        else ""
                    )
                    if upgrade_status_text:
                        if (
                            "Eligible as of" in upgrade_status_text
                            or "Admissible à partir du" in upgrade_status_text
                        ):
                            self.upgrade = self.extract_date(upgrade_status_text)
                            break
                        elif (
                            "Eligible" == upgrade_status_text
                            or "Admissible" == upgrade_status_text
                        ):
                            self.upgrade = "Yes"
                            break

                except Exception as e:
                    logging.error(str(e))
                    print(f"error checking upgrade path {upgrade_path}")

            # TODO: FINISH DRO
            self.dro = "No"
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(str(e))
            self.dro = "No"
            self.upgrade = "No"
            self.details = "FIELD NOT FOUND"

    def execute(self):
        logging.info(f"PHONE NUMBER: {self.phone_number}")
        self.check_upgrade_and_dro_status()
        details = {"upgrade": self.upgrade, "dro": self.dro, "details": self.details}
        print(details)
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
        # English months
        english_match = re.search(
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
            text,
        )
        if english_match:
            date_str = english_match.group(0)
            return datetime.strptime(date_str, "%B %d, %Y").date().isoformat()

        # French months
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
            # Replace French month with English equivalent
            for french_month, english_month in french_months.items():
                if french_month in french_date.lower():
                    english_date = french_date.lower().replace(
                        french_month, english_month
                    )
                    # Capitalize first letter of month
                    parts = english_date.split()
                    parts[0] = parts[0].capitalize()
                    english_date = " ".join(parts)
                    return (
                        datetime.strptime(english_date, "%B %d, %Y").date().isoformat()
                    )

        return None
