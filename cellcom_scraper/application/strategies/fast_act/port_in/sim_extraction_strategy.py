from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.domain.exceptions import SimExtractionException
from cellcom_scraper.config import PORT_IN_AWS_SERVER


class SimExtractionStrategy(BellFastActBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.response_server_url = PORT_IN_AWS_SERVER
        self.sim_number = None

    def search_sim_number(self):
        try:
            search_link = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/ul[1]/li[3]/a[1]",
                    )
                )
            )
            search_link.click()

            mobile_radiobtn = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[1]/div[1]/div[2]/div[2]/div[3]/input[1]",
                    )
                )
            )
            mobile_radiobtn.click()

            mobile_number_input = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[2]/div[1]/div[11]/div[2]/input[1]",
                    )
                )
            )
            mobile_number_input.send_keys(self.phone_number)

            button_next = self.wait120.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body/div[@id='instant_activation']/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[5]/div[1]/div[1]/div[1]/button[1]",
                    )
                )
            )
            button_next.click()

        except Exception:
            raise SimExtractionException("Failed searching SIM number")

        try:
            self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[2]/div[1]/div[1]/center[1]/table[1]",
                    )
                )
            )
        except Exception:
            raise SimExtractionException("Phone number not found")

        agreement_number_link = self.wait120.until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[2]/div[1]/div[1]/center[1]/table[1]/tbody[1]/tr[1]/td[4]/a[1]",
                )
            )
        )
        agreement_number_link.click()

    def get_sim_value(self):
        sim_p_1 = self.get_sim_field_xpath("4", "8", "4")
        sim_p_2 = self.get_sim_field_xpath("4", "9", "5")
        sim_p_3 = self.get_sim_field_xpath("4", "9", "4")
        sim_p_4 = self.get_sim_field_xpath("5", "9", "4")
        sim_p_5 = self.get_sim_field_xpath("6", "9", "5")
        sim_p_6 = self.get_sim_field_xpath("5", "7", "5")
        sim_p_7 = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[3]/div[1]/div[4]/div[1]/div[4]/div[2]"

        possibilities = [sim_p_1, sim_p_2, sim_p_3, sim_p_4, sim_p_5, sim_p_6, sim_p_7]
        sim_card = ""
        for possibility in possibilities:
            try:
                table_field = self.wait10.until(
                    ec.presence_of_element_located((By.XPATH, possibility))
                )
                table_text = table_field.get_attribute("innerHTML")
                if table_text and table_text != "HSPA+ / LTE / 5G":
                    sim_card = table_text
                    break
            except Exception:
                continue

        if not sim_card:
            raise SimExtractionException("SIM number not found")
        return sim_card

    @staticmethod
    def get_sim_field_xpath(div1: str, div2: str, div3: str):
        sim_generic_xpath = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[%(div1)s]/div[1]/div[1]/div[1]/div[%(div2)s]/div[%(div3)s]/div[2]"
        values = {"div1": div1, "div2": div2, "div3": div3}
        return sim_generic_xpath % values

    def execute(self):
        super().execute()
        self.search_sim_number()
        self.sim_number = self.get_sim_value()

    def handle_results(self):
        sim_card: str = self.sim_number.strip()
        data: dict = {
            "response": "Finished successfully",
            "result": "Ok",
            "process_id": self.aws_id,
            "sim_card": sim_card,
        }
        endpoint: str = "request-sim-confirmation"
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
