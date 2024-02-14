import os

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.domain.exceptions import UnknownConfigurationException

DEFAULT_DOWNLOAD_FOLDER_PATH = os.environ.get(
    "DEFAULT_DOWNLOADS_PATH", "./default/downloads"
)

CHROME_DRIVER_DEFAULT_CONFIGURATIONS: dict = {
    "arguments": [
        "--incognito",
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-webgl",
        "--disable-rtc-smoothness-algorithm",
        "--disable-dev-shm-usage",
        "--no-sandbox",
    ],
    "experimental_options": {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False,
        "prefs": {
            "download.prompt_for_download": False,
            "download.default_directory": DEFAULT_DOWNLOAD_FOLDER_PATH,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "download.manager.showWhenStarting": False,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
            "permissions.default.stylesheet": 2,
        },
    },
}

FIREFOX_DRIVER_DEFAULT_CONFIGURATIONS: dict = {
    "arguments": ["-private-window", "--start-maximized"],
    "firefox_profile": {
        "browser.download.folderList": 2,
        "browser.download.manager.showWhenStarting": False,
        "browser.helperApps.alwaysAsk.force": False,
        "browser.helperApps.neverAsk.saveToDisk": "application/x-zip-compressed;application/zip",
        "browser.download.dir": DEFAULT_DOWNLOAD_FOLDER_PATH,
        "browser.download.lastDir": DEFAULT_DOWNLOAD_FOLDER_PATH,
    },
    "preferences": {
        "browser.startup.homepage": "about:blank",
        "browser.search.suggest.enabled": False,
        "browser.startup.homepage_override.mstone": "ignore",
        "dom.webdriver.enabled": False,
        "useAutomationExtension": False,
        "toolkit.telemetry.reportingpolicy.firstRun": False,
        "webgl.disabled": True,
        "media.peerconnection.enabled": False,
    },
}

EDGE_DRIVER_DEFAULT_CONFIGURATIONS: dict = {
    "arguments": [
        "--inprivate",
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-webgl",
        "--disable-rtc-smoothness-algorithm",
    ],
    "experimental_options": {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False,
        "prefs": {
            "download.default_directory": DEFAULT_DOWNLOAD_FOLDER_PATH,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        },
    },
}


def get_webdriver_default_config(navigator_name: NavigatorWebDriverType) -> dict:
    configurations = {
        NavigatorWebDriverType.CHROME: CHROME_DRIVER_DEFAULT_CONFIGURATIONS,
        NavigatorWebDriverType.FIREFOX: FIREFOX_DRIVER_DEFAULT_CONFIGURATIONS,
        NavigatorWebDriverType.EDGE: EDGE_DRIVER_DEFAULT_CONFIGURATIONS,
    }

    if navigator_name in configurations:
        return configurations[navigator_name]
    else:
        raise UnknownConfigurationException(
            f"selected configuration for navigator {navigator_name} doesn't exist"
        )
