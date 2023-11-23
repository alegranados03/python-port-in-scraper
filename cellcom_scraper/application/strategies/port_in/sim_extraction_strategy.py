import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from cellcom_scraper.application.strategies.port_in.base_bellfast_strategy import (
    BellFastBaseStrategy,
)


class SimExtractionStrategy(BellFastBaseStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.sim_number = None

    def search_sim_number(self):
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
        time.sleep(2)

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

        try:
            self.wait30.until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        "//body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[2]/div[1]/div[1]/center[1]/table[1]",
                    )
                )
            )
        except Exception as e:
            pass  # raise phone number not found

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
        sim_p_1 = self.get_sim_field_xpath("8", "4")
        sim_p_2 = self.get_sim_field_xpath("9", "5")
        sim_p_3 = self.get_sim_field_xpath("9", "4")

        possibilities = [sim_p_1, sim_p_2, sim_p_3]
        sim_card = ""
        for possibility in possibilities:
            try:
                table_field = self.wait30.until(
                    ec.presence_of_element_located((By.XPATH, possibility))
                )
                table_text = table_field.get_attribute("innerHTML")
                if table_text and table_text != "HSPA+ / LTE / 5G":
                    sim_card = table_text
                    break
            except:
                continue

        if not sim_card:
            pass  # raise error sim not found

        return sim_card

    @staticmethod
    def get_sim_field_xpath(div1: str, div2: str):
        sim_generic_xpath = "/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/form[1]/div[4]/div[1]/div[1]/div[1]/div[%(div1)s]/div[%(div2)s]/div[2]"
        values = {"div1": div1, "div2": div2}
        return sim_generic_xpath % values

    def execute(self):
        super().execute()
        self.search_sim_number()
        self.sim_number = self.get_sim_value()
