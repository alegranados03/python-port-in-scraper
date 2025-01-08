import threading
import os

from cellcom_scraper.application.controllers import (
    PortInController,
    UpgradeAndDroController,
    VirginUpgradeAndDroController
)
from cellcom_scraper.domain.entities import (
    AccountEntity,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception


class Processor:
    def __init__(
            self
    ):
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
                username=os.getenv("BELL_FAST_USERNAME"),
                dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
                password=os.getenv("BELL_FAST_PASSWORD"),
            )
        }

        self.controllers_list: list = [
            PortInController,
            UpgradeAndDroController,
            # VirginUpgradeAndDroController
        ]

    def _get_account_credentials(self, controller: Controller):
        return self.account_credentials_dict[controller.__name__]

    def start_processor(self):
        for controller in self.controllers_list:
            self._execute_controller_process(controller)
            # for i in range(1):
            #     thread = threading.Thread(target=self._execute_controller_process, args=(controller,), daemon=False)
            #     thread.start()

    def _execute_controller_process(self, controller):
        uow = DefaultUnitOfWork()
        c: Controller = controller(uow)
        c.set_credentials(self._get_account_credentials(controller))
        try:
            c.execute()
        except Exception as e:
            print(handle_general_exception(e, f"{controller.__name__} failed at execute"))
