from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.port_in.base_bellfast_strategy import (
    BellFastBaseStrategy,
)

from cellcom_scraper.domain.exceptions import PortInNumberException


class PortInNumberStrategy(BellFastBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)

    def port_in_number(self):
        portin_dates_changes = self.wait30.until(
            ec.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'Port-In Date Changes')]")
            )
        )
        portin_dates_changes.click()

        manual_entry = self.wait30.until(
            ec.presence_of_element_located(
                (By.XPATH, "//a[contains(text(),'Manual Entry')]")
            )
        )
        manual_entry.click()

        portin_number = self.wait30.until(
            ec.presence_of_element_located(
                (By.XPATH, "//tbody/tr[@id='rowId_0']/td[1]/input[1]")
            )
        )
        portin_number.send_keys(self.phone_number)

        asap_checkbox = self.wait30.until(
            ec.presence_of_element_located(
                (By.XPATH, "//tbody/tr[@id='rowId_0']/td[6]/input[1]")
            )
        )
        asap_checkbox.click()

        validate_btn = self.wait30.until(
            ec.presence_of_element_located((By.XPATH, "//a[@id='validate']"))
        )
        validate_btn.click()

        rows = self.driver.find_elements(
            By.CSS_SELECTOR, "table > tbody tr[id*=rowId_]"
        )

        error_number_indexes = []
        for i, row in enumerate(rows):
            if row.get_attribute("style") == "color: rgb(255, 0, 0);":
                error_number_indexes.append(i)

        if len(error_number_indexes) > 0:
            pass
            error_msg = self.driver.find_element(
                By.XPATH,
                "//body/div[@id='instant_activation']/div[2]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/ul[1]/li[1]/font[1]",
            )
            raise PortInNumberException(error_msg.text)

        else:
            submit_btn = self.wait30.until(
                ec.presence_of_element_located((By.XPATH, "//a[@id='submitted']"))
            )
            submit_btn.click()

    def execute(self):
        super().execute()
        self.port_in_number()

    def handle_results(self, aws_id: int):
        screenshot = self.take_screenshot()
        data = {
            "response": "Finished successfully",
            "error_filename": screenshot["error_filename"],
            "error_screenshot": screenshot["error_screenshot"],
            "process_id": aws_id,
        }
        endpoint: str = "reply-results"
        self.send_to_aws(data, endpoint)
