import logging


from cellcom_scraper.application.controllers.fast_act_controller import (
    FastActController,
)
from cellcom_scraper.config import FORCE_STOP_ERRORS, UPGRADE_AND_DRO_MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import (
    ApplicationException,
    CloseButtonNotFoundException,
)
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from cellcom_scraper.domain.enums import RequestStatus, RequestType


class UpgradeAndDroController(FastActController):
    def __init__(self, uow: UnitOfWork):
        super().__init__(uow)

    def _get_request(self) -> None:
        try:
            self.request = self.uow.get_repository(
                "process_requests"
            ).filter_with_skip_locked(
                limit=1,
                status=RequestStatus.READY.value,
                scraper_id=2,
                type=RequestType.UPGRADE_STATUS_AND_DRO.value
            )
        except Exception as e:
            print(
                handle_general_exception(
                    e, f"Requests fetch on {self.__class__.__name__} failed"
                )
            )
            logging.error(f"Requests fetch on {self.__class__.__name__} failed")

    def execute(self):
        # print(f"{self.__class__.__name__} thread ready to start.")
        while True:
            with self.uow:
                # print(f"{self.__class__.__name__} thread started a session.")
                try:
                    transaction = self.uow.session.begin()
                    # print(f"{self.__class__.__name__} thread started a database transaction.")
                    self._get_request()
                    if not self.request:
                        break

                    # print(f"{self.__class__.__name__} thread is processing record {self.request.id}")

                    request_type: RequestType = RequestType(self.request.type)
                    self.set_strategy(request_type)
                    self.strategy.set_phone_number(self.request.number_to_port)
                    self.strategy.set_aws_id(self.request.aws_id)
                    tries = 0
                    while tries < UPGRADE_AND_DRO_MAX_ATTEMPTS:
                        try:
                            self.set_environment()
                            self.strategy.set_driver(self.builder.get_driver())
                            self.strategy.execute()
                            self.handle_results()
                            tries = UPGRADE_AND_DRO_MAX_ATTEMPTS + 1
                            self._update_request_status(
                                request=self.request, status=RequestStatus.FINISHED
                            )
                            transaction.commit()
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
                            self.driver.close()
                        except ApplicationException as e:
                            tries = tries + 1
                            for error in FORCE_STOP_ERRORS:
                                if error in str(e):
                                    tries = UPGRADE_AND_DRO_MAX_ATTEMPTS
                                    break
                            if tries == UPGRADE_AND_DRO_MAX_ATTEMPTS:
                                self._update_request_status(
                                    request=self.request, status=RequestStatus.ERROR
                                )
                                self.handle_errors(
                                    description=e.message, details=e.traceback
                                )
                            try:
                                if self.webdriver_is_active():
                                    self.click_screen_close_button()
                            except CloseButtonNotFoundException as e:
                                self.driver.close()
                        except Exception as e:
                            tries = tries + 1
                            message = f"Another type of exception occurred for this request id: {self.request.id}, please report this to the administrator if it occurs more than one time"
                            full_error_message = handle_general_exception(e, message)
                            print(full_error_message)
                            logging.error(message)
                            logging.error(full_error_message)
                            if tries == UPGRADE_AND_DRO_MAX_ATTEMPTS:
                                self._update_request_status(
                                    request=self.request, status=RequestStatus.ERROR
                                )
                                self.handle_errors(
                                    description=message, details=full_error_message
                                )
                except Exception as e:
                    logging.error(f"{self.__class__.__name__}: Thread error: {e}")
                    transaction.rollback()
                finally:
                    print(f"{self.__class__.__name__}: Thread FINISHED.")
                    transaction.close()
