import time
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
                        type=RequestType.UPGRADE_STATUS_AND_DRO.value,
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

    def execute(self):
        logging.info(f"{self.__class__.__name__}: Starting execute loop")
        while True:
            self._get_request()
            if not self.request:
                logging.debug(f"{self.__class__.__name__}: No more requests to process, exiting loop")
                break
            try:
                logging.info(f"{self.__class__.__name__}: Processing request {self.request.id}")
                request_type: RequestType = RequestType(self.request.type)
                logging.debug(f"{self.__class__.__name__}: Request type identified as {request_type.name}")
                self.set_strategy(request_type)
                self.strategy.set_phone_number(self.request.number_to_port)
                self.strategy.set_aws_id(self.request.aws_id)
                logging.debug(f"{self.__class__.__name__}: Strategy configured for phone {self.request.number_to_port}")
                tries = 0
                while tries < UPGRADE_AND_DRO_MAX_ATTEMPTS:
                    try:
                        logging.info(f"{self.__class__.__name__}: Attempt {tries + 1} of {UPGRADE_AND_DRO_MAX_ATTEMPTS} for request {self.request.id}")
                        self.set_environment()
                        self.strategy.set_driver(self.builder.get_driver())
                        self.strategy.execute()
                        self.handle_results()
                        tries = UPGRADE_AND_DRO_MAX_ATTEMPTS + 1
                        self._update_request_status(
                            request=self.request, status=RequestStatus.FINISHED
                        )
                        logging.info(f"{self.__class__.__name__}: Request {self.request.id} completed successfully")
                        if self.webdriver_is_active():
                            self.click_screen_close_button()
                    except CloseButtonNotFoundException as e:
                        logging.warning(f"{self.__class__.__name__}: Close button not found for request {self.request.id}, closing driver")
                        self.driver.close()
                    except ApplicationException as e:
                        tries = tries + 1
                        logging.warning(f"{self.__class__.__name__}: ApplicationException on attempt {tries} for request {self.request.id}: {e.message}")
                        for error in FORCE_STOP_ERRORS:
                            if error in str(e):
                                logging.error(f"{self.__class__.__name__}: Force stop error detected: {error}")
                                tries = UPGRADE_AND_DRO_MAX_ATTEMPTS
                        if tries == UPGRADE_AND_DRO_MAX_ATTEMPTS:
                            self._update_request_status(
                                request=self.request, status=RequestStatus.ERROR
                            )
                            logging.error(f"{self.__class__.__name__}: Request {self.request.id} marked as ERROR after max attempts")
                            self.handle_errors(
                                description=e.message, details=e.traceback
                            )
                        try:
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
                            logging.warning(f"{self.__class__.__name__}: Close button not found after error on request {self.request.id}")
                            self.driver.close()
                    except Exception as e:
                        tries = tries + 1
                        message = f"Another type of exception occurred for this request id: {self.request.id}, please report this to the administrator if it occurs more than one time"
                        full_error_message = handle_general_exception(e, message)
                        logging.error(f"{self.__class__.__name__}: Unexpected exception on attempt {tries} for request {self.request.id}: {full_error_message}", exc_info=True)
                        print(full_error_message)
                        if tries == UPGRADE_AND_DRO_MAX_ATTEMPTS:
                            self._update_request_status(
                                request=self.request, status=RequestStatus.ERROR
                            )
                            logging.error(f"{self.__class__.__name__}: Request {self.request.id} marked as ERROR")
                            self.handle_errors(
                                description=message, details=full_error_message
                            )
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Thread error: {e}", exc_info=True)
            finally:
                logging.debug(f"{self.__class__.__name__}: Thread FINISHED.")
