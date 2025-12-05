import threading
import logging

from cellcom_scraper.application.controllers import (
    PortInController,
    UpgradeAndDroController,
    VirginUpgradeAndDroController,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self):
        logger.info("Initializing Processor with controllers")
        self.controllers_list: list = [
            PortInController,
            UpgradeAndDroController,
            VirginUpgradeAndDroController,
        ]
        logger.debug(f"Loaded {len(self.controllers_list)} controllers: {[c.__name__ for c in self.controllers_list]}")

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
        logger.debug(f"Controller {controller.__name__} instantiated")
        try:
            logger.info(f"Executing {controller.__name__}")
            c.execute()
            logger.info(f"{controller.__name__} executed successfully")
        except Exception as e:
            error_message = handle_general_exception(e, f"{controller.__name__} failed at execute")
            logger.error(error_message, exc_info=True)
            print(error_message)
