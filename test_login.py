from dotenv import load_dotenv
import os
import time

load_dotenv()

from cellcom_scraper.domain.entities.account import AccountEntity
from cellcom_scraper.application.strategies.fast_act.base_bellfast_strategy import (
    BellFastActBaseStrategy,
)
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import (
    AccountEntity,
    ScraperEntity,
)

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
base_scraper = BellFastActBaseStrategy(credentials)

builder = get_webdriver_builder(navigator, scraper.url)
builder.set_driver_options(options={})
builder.initialize_driver()
base_scraper.set_credentials(credentials)
driver = builder.get_driver()
base_scraper.set_driver(builder.get_driver())

browser_info_script = """
    return {
        webdriver: navigator.webdriver,
        languages: navigator.languages,
        pluginsLength: navigator.plugins.length,
        platform: navigator.platform,
        userAgent: navigator.userAgent,
        webdriver: !!navigator.webdriver,
        areCookiesEnabled: navigator.cookieEnabled,
        screenSize: {
            width: screen.width,
            height: screen.height
        }
        }
        """
info = driver.execute_script(browser_info_script)
print(info)


base_scraper.login()

time.sleep(10)
builder.get_driver().close()
