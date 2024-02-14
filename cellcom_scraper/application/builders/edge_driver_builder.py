from selenium import webdriver

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from settings.navigator_default_configurations import get_webdriver_default_config
import time


class EdgeDriverBuilder(AutomationDriverBuilder):
    def __init__(self, url=None):
        self.url = url
        self.options = None
        self.driver = None

    def set_url(self, url):
        self.url = url

    def set_driver_options(self, **kwargs):
        experimental_options = "experimental_options"
        options = kwargs["options"]
        default_options = get_webdriver_default_config(NavigatorWebDriverType.EDGE)
        if options:
            options = {**default_options, **options}
        else:
            options = default_options
        arguments = "arguments"
        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        if arguments in options and isinstance(options[arguments], list):
            for argument in options[arguments]:
                edge_options.add_argument(argument)

        if experimental_options in options and isinstance(
            options[experimental_options], dict
        ):
            for option, values in options[experimental_options].items():
                edge_options.add_experimental_option(option, values)

        self.options = edge_options

    def initialize_driver(self):
        driver = webdriver.Edge(options=self.options)
        self.driver = driver
        time.sleep(5)
        self.driver.get(self.url)
