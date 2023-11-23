from abc import ABC, abstractmethod

from cellcom_scraper.domain.enums import RequestType


class Scraper(ABC):
    @abstractmethod
    def set_automation_driver_builder(self, builder):
        raise NotImplementedError

    @abstractmethod
    def set_strategy(self, scraper_name: RequestType):
        raise NotImplementedError

    @abstractmethod
    def set_phone_number(self, set_phone_number: str):
        raise NotImplementedError

    @abstractmethod
    def execute(self, navigator_options: dict):
        raise NotImplementedError

    @abstractmethod
    def set_credentials(self, credentials):
        raise NotImplementedError
