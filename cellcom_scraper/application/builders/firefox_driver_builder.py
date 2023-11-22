from selenium import webdriver

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from settings.navigator_default_configurations import get_webdriver_default_config


class FirefoxDriverBuilder(AutomationDriverBuilder):
    def __init__(self, url=None):
        self.url = url
        self.options = None
        self.driver = None

    def set_url(self, url):
        self.url = url

    def set_driver_options(self, **kwargs):
        options = kwargs["options"]
        default_options = get_webdriver_default_config(NavigatorWebDriverType.FIREFOX)
        if options:
            options = {**default_options, **options}
        else:
            options = default_options
        firefox_profile = "firefox_profile"
        arguments = "arguments"
        preferences = "preferences"
        firefox_options = webdriver.FirefoxOptions()

        if arguments in options and isinstance(options[arguments], list):
            for argument in options[arguments]:
                firefox_options.add_argument(argument)

        if firefox_profile in options and isinstance(options[firefox_profile], dict):
            fp = webdriver.FirefoxProfile()
            for pref, value in options[firefox_profile].items():
                fp.set_preference(pref, value)
            firefox_options.profile = fp

        if preferences in options and isinstance(options[preferences], dict):
            for pref, value in options[preferences].items():
                firefox_options.set_preference(pref, value)

        self.options = firefox_options

    def initialize_driver(self):
        driver = webdriver.Firefox(options=self.options)
        self.driver = driver
        self.driver.get(self.url)
