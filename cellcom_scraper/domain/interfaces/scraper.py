from abc import ABC, abstractmethod


class Scraper(ABC):
    @abstractmethod
    def set_automation_driver_builder(self, builder):
        raise NotImplementedError

    @abstractmethod
    def set_strategy(self, scraper_name: str):
        raise NotImplementedError

    @abstractmethod
    def execute(self, extras: dict, navigator_options: dict):
        raise NotImplementedError

    @abstractmethod
    def set_credentials(self, credentials):
        raise NotImplementedError
