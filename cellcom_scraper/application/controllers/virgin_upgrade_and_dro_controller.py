from cellcom_scraper.application.controllers.upgrade_and_dro_controller import (
    UpgradeAndDroController,
)
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as ec
from cellcom_scraper.domain.exceptions import (
    CloseButtonNotFoundException,
)
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.common.exceptions import NoAlertPresentException
import logging


class VirginUpgradeAndDroController(UpgradeAndDroController):
    def _get_request(self) -> None:
        try:
            logging.debug(f"{self.__class__.__name__}: Attempting to retrieve next request")
            with self.uow:
                transaction = self.uow.session.begin()
                try:
                    self.request = self.uow.get_repository(
                        "process_requests"
                    ).filter_with_skip_locked(
                        limit=1,
                        status=RequestStatus.READY.value,
                        scraper_id=2,
                        type=RequestType.VIRGIN_UPGRADE_STATUS_AND_DRO.value,
                    )
                    if self.request:
                        logging.info(f"{self.__class__.__name__}: Request fetched with ID {self.request.id}, phone number: {self.request.number_to_port}")
                        self._update_request_status_without_commit(
                            request=self.request, status=RequestStatus.IN_PROGRESS
                        )
                        logging.debug(f"{self.__class__.__name__}: Request status updated to IN_PROGRESS")
                    else:
                        logging.debug(f"{self.__class__.__name__}: No ready requests found")
                    transaction.commit()
                except Exception as e:
                    logging.error(f"{self.__class__.__name__}: Error occurred on request transaction - {str(e)}")
                    transaction.close()
        except Exception as e:
            error_message = handle_general_exception(
                e, f"Requests fetch on {self.__class__.__name__} failed"
            )
            print(error_message)
            logging.error(f"Requests fetch on {self.__class__.__name__} failed - {error_message}", exc_info=True)

    def click_screen_close_button(self):
        logging.debug(f"{self.__class__.__name__}: Redirecting to Virgin Plus OneView")
        self.driver.get("https://oneview.virginplus.ca/RFEApp/Shared/Ng9Index.html")
        logging.debug(f"{self.__class__.__name__}: Redirect completed")
