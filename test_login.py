import os
import time

from dotenv import load_dotenv

load_dotenv()

from selenium.common.exceptions import WebDriverException

from cellcom_scraper.application.controllers.fast_act_controller import (
    FastActController,
)
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import AccountEntity, ScraperEntity
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork


def webdriver_esta_activo(driver):
    try:
        if driver.window_handles:
            return True
        else:
            return False
    except WebDriverException:
        return False


credentials = AccountEntity(
    username=os.getenv("BELL_FAST_USERNAME"),
    dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
    password=os.getenv("BELL_FAST_PASSWORD"),
)
navigator = NavigatorWebDriverType.CHROME
scraper = ScraperEntity(
    id=1,
    url=os.environ.get("FAST_ACT_URL"),
    slug="port_in_scraper",
    name="Port In Scraper",
    available=1,
)
uow = DefaultUnitOfWork()
controller = FastActController(uow)

try:
    controller.set_environment()
    print("la ventana está abierta: ", webdriver_esta_activo(controller.driver))
    raise Exception
except Exception as e:
    print("la ventana sigue abierta: ", webdriver_esta_activo(controller.driver))

time.sleep(10)
# browser_info_script = """
#     return {
#         webdriver: navigator.webdriver,
#         languages: navigator.languages,
#         pluginsLength: navigator.plugins.length,
#         platform: navigator.platform,
#         userAgent: navigator.userAgent,
#         webdriver: !!navigator.webdriver,
#         areCookiesEnabled: navigator.cookieEnabled,
#         screenSize: {
#             width: screen.width,
#             height: screen.height
#         }
#         }
#         """
# info = controller.driver.execute_script(browser_info_script)
# print(info)
# with uow:
#     print(uow.get_repository("process_requests").filter(status="READY", scraper_id=1))
