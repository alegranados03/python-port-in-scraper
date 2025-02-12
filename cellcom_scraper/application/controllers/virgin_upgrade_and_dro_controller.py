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
            self.request = self.uow.get_repository(
                "process_requests"
            ).filter_with_skip_locked(
                limit=1,
                status=RequestStatus.READY.value,
                scraper_id=2,
                type=RequestType.VIRGIN_UPGRADE_STATUS_AND_DRO.value,
            )
        except Exception as e:
            print(
                handle_general_exception(
                    e, "Requests fetch on VirginUpgradeAndDroController failed"
                )
            )

    def click_screen_close_button(self):
        option_1 = (
            "/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div/a[1]"
        )

        close_options = [option_1]
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
            raise CloseButtonNotFoundException("Finished without close button")
