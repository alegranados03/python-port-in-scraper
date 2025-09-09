import os
import time

from dotenv import load_dotenv

load_dotenv()

from selenium.common.exceptions import WebDriverException

from cellcom_scraper.application.controllers.fast_act_controller import (
    FastActController,
)
from cellcom_scraper.application.controllers import (
    PortInController,
    UpgradeAndDroController,
    VirginUpgradeAndDroController
)
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import AccountEntity, ScraperEntity
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from selenium.webdriver.support.ui import WebDriverWait
from cellcom_scraper.application.strategies.fast_act.port_in.sim_extraction_strategy import SimExtractionStrategy
from cellcom_scraper.application.strategies.fast_act.upgrade_and_dro.virgin_upgrade_and_dro_strategy import VirginUpgradeAndDroStrategy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


def webdriver_esta_activo(driver):
    try:
        if driver.window_handles:
            return True
        else:
            return False
    except WebDriverException:
        return False


credentials = AccountEntity(
    username=os.getenv("VIRGIN_USERNAME"),
    dealer_code=os.getenv("VIRGIN_DEALER_CODE"),
    password=os.getenv("VIRGIN_PASSWORD"),
)
navigator = NavigatorWebDriverType.EDGE
scraper = ScraperEntity(
    id=1,
    url=os.environ.get("FAST_ACT_URL"),
    slug="port_in_scraper",
    name="Port In Scraper",
    available=1,
)
uow = DefaultUnitOfWork()
controller = VirginUpgradeAndDroController(uow)

wait30 = WebDriverWait(controller.driver, 30)
controller.set_credentials(credentials)
controller.set_environment()
strategy = VirginUpgradeAndDroStrategy(credentials)
number = '4372247632'
strategy.set_driver(controller.driver)
strategy.set_phone_number(number)

def search_sim():
    strategy.search_sim_number()

    users = controller.driver.find_elements(By.CSS_SELECTOR, '#user_data')


    for user in users:
        labels = user.find_elements(By.CLASS_NAME, 'fLabel2')
        for label in labels:
            if 'Phone Number:' in label.text:
                phone_number_element = label.find_element(By.XPATH, 'following-sibling::div[@class="fWidget"]')
                phone_number = phone_number_element.text.strip()

                if phone_number == number:
                    print(f"Teléfono encontrado: {phone_number}")
                    sim_label = user.find_element(By.XPATH, ".//div[contains(., 'SIM:')]/following-sibling::div[@class='fWidget']")
                    sim_number = sim_label.text.strip()
                    print(f"Número SIM correspondiente: {sim_number}")
                    break


strategy.execute()
#time.sleep(10)
controller.click_screen_close_button()
time.sleep(10)
