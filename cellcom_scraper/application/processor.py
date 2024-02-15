import logging
import os
from datetime import datetime
from typing import List, Optional

from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.application.selectors import get_webdriver_builder
from cellcom_scraper.domain.entities import (
    AccountEntity,
    ProcessQueueRequestEntity,
    ScraperEntity,
)
from cellcom_scraper.domain.entities.process_queue_request import (
    ProcessQueueUpdateEntity,
)
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.domain.interfaces.automation_driver_builder import (
    AutomationDriverBuilder,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from cellcom_scraper.application.controllers.fast_act_controller import (
    FastActController,
)
from cellcom_scraper.domain.enums import ScraperControllerType
from cellcom_scraper.domain.exceptions import UnknownControllerException


class Processor:
    def __init__(
        self,
        uow: UnitOfWork,
        account_credentials: AccountEntity,
    ):
        self.uow: UnitOfWork = uow
        self.account_credentials: AccountEntity = account_credentials
        self.controllers_list: list = [FastActController]

    def _get_account_credentials(self):
        return self.account_credentials

    def start_processor(self):
        for controller in self.controllers_list:
            c: Controller = controller(self.uow)
            print(self._get_account_credentials())
            c.set_credentials(self._get_account_credentials())
            c.execute()
