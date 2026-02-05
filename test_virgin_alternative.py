import os
import time

from dotenv import load_dotenv

load_dotenv()

from selenium.common.exceptions import WebDriverException

from cellcom_scraper.application.controllers import (
    PortInController,
)
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.domain.entities import AccountEntity, ScraperEntity
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from selenium.webdriver.support.ui import WebDriverWait
from cellcom_scraper.application.strategies.fast_act.upgrade_and_dro.virgin_upgrade_and_dro_strategy_alternative import (
    VirginUpgradeAndDroStrategyAlternative,
)
from selenium.webdriver.common.by import By


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
controller = PortInController(uow)

wait30 = WebDriverWait(controller.driver, 30)
controller.set_credentials(credentials)
controller.set_environment()
strategy = VirginUpgradeAndDroStrategyAlternative(credentials)
number = "4372247632"
strategy.set_driver(controller.driver)
strategy.set_phone_number(number)


strategy.execute()
# time.sleep(10)
controller.click_screen_close_button()
time.sleep(10)
