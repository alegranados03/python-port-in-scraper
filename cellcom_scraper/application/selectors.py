from typing import TypeVar

from cellcom_scraper.application.builders.chrome_driver_builder import \
    ChromeDriverBuilder
from cellcom_scraper.application.builders.edge_driver_builder import \
    EdgeDriverBuilder
from cellcom_scraper.application.builders.firefox_driver_builder import \
    FirefoxDriverBuilder
from cellcom_scraper.application.enums import (NavigatorWebDriverType,
                                               StrategyName)
from cellcom_scraper.application.strategies.bell import (
    BellAccountMonthReportsStrategy, BellDailyUsageStrategy)
from cellcom_scraper.application.strategies.telus import (TelusBillReport,
                                                          TelusDailyUsage)
from cellcom_scraper.domain.enums import ExecutionFrequency
from cellcom_scraper.domain.exceptions import (UnknownNavigatorException,
                                               UnknownStrategyException)
from cellcom_scraper.domain.interfaces.automation_driver_builder import \
    AutomationDriverBuilder

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


def get_scraper_strategy(strategy_name: StrategyName):
    strategies_list = {
        StrategyName.BELL_DAILY_USAGE: lambda credentials: BellDailyUsageStrategy(
            credentials
        ),
        StrategyName.BELL_MONTHLY_REPORTS: lambda credentials: BellAccountMonthReportsStrategy(
            credentials
        ),
        StrategyName.TELUS_DAILY_USAGE: lambda credentials: TelusDailyUsage(
            credentials
        ),
        StrategyName.TELUS_BILL_REPORT: lambda credentials: TelusBillReport(
            credentials
        ),
    }

    if strategy_name in strategies_list:
        return strategies_list[strategy_name]
    else:
        raise UnknownStrategyException(
            f"Selected strategy {strategy_name} doesn't exist"
        )


def get_time_deltas(execution_frequency: ExecutionFrequency):
    deltas = {
        ExecutionFrequency.ONCE: 0,
        ExecutionFrequency.DAILY: 1,
        ExecutionFrequency.MONTHLY: 30,
    }

    if execution_frequency in deltas:
        return deltas[execution_frequency]
    else:
        raise UnknownStrategyException(
            f"Selected execution frequency {execution_frequency} doesn't exist"
        )
