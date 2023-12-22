from typing import TypeVar

from cellcom_scraper.application.builders.chrome_driver_builder import (
    ChromeDriverBuilder,
)
from cellcom_scraper.application.builders.edge_driver_builder import EdgeDriverBuilder
from cellcom_scraper.application.builders.firefox_driver_builder import (
    FirefoxDriverBuilder,
)
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.strategies.port_in import (
    PortInNumberStrategy,
    SimExtractionStrategy,
    PortInViaFicticeNumberStrategy,
)
from cellcom_scraper.domain.enums import RequestType
from cellcom_scraper.domain.exceptions import (
    UnknownNavigatorException,
    UnknownStrategyException,
)
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)

DriverBuilder = TypeVar("DriverBuilder", bound=AutomationDriverBuilder)


def get_webdriver_builder(navigator_name: NavigatorWebDriverType) -> DriverBuilder:
    builders = {
        NavigatorWebDriverType.CHROME: ChromeDriverBuilder,
        NavigatorWebDriverType.FIREFOX: FirefoxDriverBuilder,
        NavigatorWebDriverType.EDGE: EdgeDriverBuilder,
    }
    if navigator_name in builders:
        return builders[navigator_name]
    else:
        raise UnknownNavigatorException(
            f"Selected navigator {navigator_name} doesn't exist"
        )


def get_scraper_strategy(strategy_name: RequestType):
    strategies_list = {
        RequestType.SIM_EXTRACTION: lambda credentials: SimExtractionStrategy(
            credentials
        ),
        RequestType.PORT_IN_NUMBER: lambda credentials: PortInNumberStrategy(
            credentials
        ),
        RequestType.PORT_IN_VIA_FICTIVE_NUMBER: lambda credentials: PortInViaFicticeNumberStrategy(
            credentials
        ),
    }

    if strategy_name in strategies_list:
        return strategies_list[strategy_name]
    else:
        raise UnknownStrategyException(
            f"Selected strategy {strategy_name} doesn't exist"
        )
