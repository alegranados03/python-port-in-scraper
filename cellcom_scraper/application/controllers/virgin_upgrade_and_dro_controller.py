from cellcom_scraper.application.controllers.upgrade_and_dro_controller import (
    UpgradeAndDroController,
)
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception
from cellcom_scraper.domain.enums import RequestStatus, RequestType


class VirginUpgradeAndDroController(UpgradeAndDroController):
    def _get_request(self) -> None:
        try:
            self.request = self.uow.get_repository(
                "process_requests"
            ).filter_with_skip_locked(
                limit=1,
                status=RequestStatus.READY.value,
                scraper_id=2,
                type=RequestType.VIRGIN_UPGRADE_STATUS_AND_DRO.value
            )
        except Exception as e:
            print(
                handle_general_exception(
                    e, "Requests fetch on VirginUpgradeAndDroController failed"
                )
            )
