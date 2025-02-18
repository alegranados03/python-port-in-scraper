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
            with self.uow:
                transaction = self.uow.session.begin()
                try:
                    self.request = self.uow.get_repository(
                        "process_requests"
                    ).filter_with_skip_locked(
                        limit=1,
                        status=RequestStatus.READY.value,
                        scraper_id=2,
                        type=RequestType.VIRGIN_UPGRADE_STATUS_AND_DRO.value
                    )
                    if self.request:
                        self._update_request_status_without_commit(
                            request=self.request, status=RequestStatus.IN_PROGRESS
                        )
                    transaction.commit()
                except Exception as e:
                    logging.error("Error occurred on request transaction")
                    transaction.close()
        except Exception as e:
            print(
                handle_general_exception(
                    e, f"Requests fetch on {self.__class__.__name__} failed"
                )
            )
            logging.error(f"Requests fetch on {self.__class__.__name__} failed")

    def click_screen_close_button(self):
        option_1 = (
            "/html[1]/body[1]/div[1]/div[1]/div[1]/div[3]/div[1]/ul[1]/li[3]/a[1]"
        )
        option_2 = (
            "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]"
        )

        close_options = [option_1, option_2]
        close = None
        for option in close_options:
            try:
                close = self.wait30.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            option,
                        )
                    )
                )
                close.click()

                try:
                    alert = self.wait30.until(ec.alert_is_present())
                    time.sleep(5)
                    alert.accept()
                except NoAlertPresentException:
                    pass
                break
            except (NoSuchElementException, TimeoutException) as e:
                message = f"{option} button not found"
                logging.error(e)
                logging.error(message)

        if not close:
            logging.error("Close button not found, forced close")
            raise CloseButtonNotFoundException("Finished without close button")
