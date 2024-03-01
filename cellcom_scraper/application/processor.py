from cellcom_scraper.application.controllers import (
    PortInController,
    UpgradeAndDroController,
)
from cellcom_scraper.domain.entities import (
    AccountEntity,
)
from cellcom_scraper.domain.interfaces.controller import Controller
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception


class Processor:
    def __init__(
        self,
        uow: UnitOfWork,
        account_credentials: AccountEntity,
    ):
        self.uow: UnitOfWork = uow
        self.account_credentials: AccountEntity = account_credentials
        self.controllers_list: list = [PortInController, UpgradeAndDroController]

    def _get_account_credentials(self):
        return self.account_credentials

    def start_processor(self):
        for controller in self.controllers_list:
            c: Controller = controller(self.uow)
            c.set_credentials(self._get_account_credentials())
            try:
                c.execute()
            except Exception as e:
                print(handle_general_exception(e, "Controller failed at execute"))
