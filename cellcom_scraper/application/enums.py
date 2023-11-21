from enum import Enum


class NavigatorWebDriverType(str, Enum):
    CHROME = "Chrome"
    FIREFOX = "Firefox"
    EDGE = "Edge"


class StrategyName(str, Enum):
    BELL_DAILY_USAGE = "bell_daily_usage"
    BELL_MONTHLY_REPORTS = "bell_monthly_reports"
    TELUS_DAILY_USAGE = "telus_daily_usage"
    TELUS_BILL_REPORT = "telus_bill_report"
