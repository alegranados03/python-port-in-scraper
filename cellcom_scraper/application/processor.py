import threading
import os
import logging

from cellcom_scraper.application.controllers import (
    PortInController,
    UpgradeAndDroController,
    VirginUpgradeAndDroController,
)
from cellcom_scraper.domain.entities import (
    AccountEntity,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self):
        logger.info("Initializing Processor with controllers and credentials")
        self.account_credentials_dict: dict = {
            PortInController.__name__: AccountEntity(
                username=os.getenv("BELL_FAST_USERNAME"),
                dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
                password=os.getenv("BELL_FAST_PASSWORD"),
            ),
            UpgradeAndDroController.__name__: AccountEntity(
                username=os.getenv("BELL_FAST_USERNAME"),
                dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
                password=os.getenv("BELL_FAST_PASSWORD"),
            ),
            VirginUpgradeAndDroController.__name__: AccountEntity(
                username=os.getenv("VIRGIN_USERNAME"),
                dealer_code=os.getenv("VIRGIN_DEALER_CODE"),
                password=os.getenv("VIRGIN_PASSWORD"),
            ),
        }
        logger.debug(f"Credentials configured for {len(self.account_credentials_dict)} controllers")

        self.controllers_list: list = [
            PortInController,
            UpgradeAndDroController,
            VirginUpgradeAndDroController,
        ]
        logger.debug(f"Loaded {len(self.controllers_list)} controllers: {[c.__name__ for c in self.controllers_list]}")

    def _get_account_credentials(self, controller: Controller):
        credentials = self.account_credentials_dict[controller.__name__]
        logger.debug(f"Retrieved credentials for controller: {controller.__name__}")
        return credentials

    def start_processor(self):
        logger.info("Starting processor - initiating controller execution sequence")
        for controller in self.controllers_list:
            logger.info(f"Processing controller: {controller.__name__}")
            self._execute_controller_process(controller)
            # for i in range(1):
            #     thread = threading.Thread(target=self._execute_controller_process, args=(controller,), daemon=False)
            #     thread.start()
        logger.info("Processor completed execution of all controllers")

    def _execute_controller_process(self, controller):
        logger.debug(f"Initializing UnitOfWork for {controller.__name__}")
        uow = DefaultUnitOfWork()
        c: Controller = controller(uow)
        c.set_credentials(self._get_account_credentials(controller))
        logger.debug(f"Credentials set for {controller.__name__}")
        try:
            logger.info(f"Executing {controller.__name__}")
            c.execute()
            logger.info(f"{controller.__name__} executed successfully")
        except Exception as e:
            error_message = handle_general_exception(e, f"{controller.__name__} failed at execute")
            logger.error(error_message, exc_info=True)
            print(error_message)
