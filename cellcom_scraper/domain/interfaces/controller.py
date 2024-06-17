from abc import ABC, abstractmethod

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.domain.entities import ScraperEntity
from cellcom_scraper.domain.enums import RequestType


class Controller(ABC):
    @abstractmethod
    def set_automation_driver_builder(self, builder):
        raise NotImplementedError

    @abstractmethod
    def set_strategy(self, scraper_name: RequestType):
        raise NotImplementedError

    @abstractmethod
    def set_credentials(self, credentials):
        raise NotImplementedError

    @abstractmethod
    def _get_account_credentials(self):
        raise NotImplementedError

    @abstractmethod
    def handle_results(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def handle_errors(self, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @abstractmethod
    def _get_scraper(self, scraper_id) -> ScraperEntity:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _get_navigator() -> NavigatorWebDriverType:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def check_system_resources() -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def _update_request_status(self, *, request, status) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_requests(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_driver(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_environment(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def login(self):
        raise NotImplementedError
