import time
import logging

from cellcom_scraper.application.controllers.fast_act_controller import (
    FastActController,
)
from cellcom_scraper.config import FORCE_STOP_ERRORS, MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import (
    ApplicationException,
    CloseButtonNotFoundException,
)
from cellcom_scraper.domain.enums import RequestStatus, RequestType
from cellcom_scraper.domain.interfaces.uow import UnitOfWork
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception


class PortInController(FastActController):
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
                        order_by="type",
                        status=RequestStatus.READY.value,
                        scraper_id=1,
                    )
                    if self.request:
                        logging.info(f"{self.__class__.__name__}: Request fetched with ID {self.request.id}, number_to_port: {self.request.number_to_port}")
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
                e, "Requests fetch on Port In Controller failed"
            )
            print(error_message)
            logging.error(f"Requests fetch on {self.__class__.__name__} failed - {error_message}", exc_info=True)

    def _handle_request_type_change(self, request_type: RequestType) -> None:
        new_credentials = self._get_credentials_by_request_type(request_type)
        new_url = self._get_url_by_request_type(request_type)

        # Check if credentials or URL changed, not just request type
        if self.current_request_type != request_type:
            current_credentials = self._get_credentials_by_request_type(self.current_request_type) if self.current_request_type else None
            current_url = self._get_url_by_request_type(self.current_request_type) if self.current_request_type else None

            if current_credentials != new_credentials or current_url != new_url:
                logging.info(f"{self.__class__.__name__}: Session change needed from {self.current_request_type} to {request_type.name} (credentials_changed={current_credentials != new_credentials}, url_changed={current_url != new_url})")
                # If there was a previous request type and driver is active, logout
                if self.current_request_type is not None and self.webdriver_is_active():
                    logging.info(f"{self.__class__.__name__}: Logging out from previous session")
                    try:
                        if self.webdriver_is_active():
                            self.click_screen_close_button()
                            self.driver.close()
                    except Exception as e:
                        logging.warning(f"{self.__class__.__name__}: Error closing previous session: {str(e)}")
                        self.driver.close() if self.webdriver_is_active() else None

                # Update credentials and URL
                self.set_credentials(new_credentials)
                self.fast_act_url = new_url
                logging.info(f"{self.__class__.__name__}: Credentials and URL updated for request type {request_type.name}")
            else:
                logging.debug(f"{self.__class__.__name__}: Request type changed but credentials and URL remain the same, maintaining current session")

            self.current_request_type = request_type
        else:
            logging.debug(f"{self.__class__.__name__}: Request type unchanged, maintaining current session")

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

                self._handle_request_type_change(request_type)

                self.set_strategy(request_type)
                self.strategy.set_phone_number(self.request.number_to_port)
                self.strategy.set_aws_id(self.request.aws_id)
                logging.debug(f"{self.__class__.__name__}: Strategy configured for phone {self.request.number_to_port}")
                tries = 0
                while tries < MAX_ATTEMPTS:
                    try:
                        logging.info(f"{self.__class__.__name__}: Attempt {tries + 1} of {MAX_ATTEMPTS} for request {self.request.id}")
                        self.set_environment()
                        self.strategy.set_driver(self.builder.get_driver())
                        self.strategy.execute()
                        self.handle_results()
                        tries = MAX_ATTEMPTS + 1
                        self._update_request_status(
                            request=self.request, status=RequestStatus.FINISHED
                        )
                        logging.info(f"{self.__class__.__name__}: Request {self.request.id} completed successfully")
                        try:
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
                            logging.warning(f"{self.__class__.__name__}: Close button not found for request {self.request.id}")
                            self.handle_errors(
                                error_description=e.message,
                                send_sms="yes",
                                send_client_sms="no",
                            )
                            self.driver.close()
                    except ApplicationException as e:
                        tries = tries + 1
                        logging.warning(f"{self.__class__.__name__}: ApplicationException on attempt {tries} for request {self.request.id}: {e.message}")
                        for error in FORCE_STOP_ERRORS:
                            if error in str(e):
                                logging.error(f"{self.__class__.__name__}: Force stop error detected: {error}")
                                tries = MAX_ATTEMPTS
                        if tries == MAX_ATTEMPTS:
                            self._update_request_status(
                                request=self.request, status=RequestStatus.ERROR
                            )
                            logging.error(f"{self.__class__.__name__}: Request {self.request.id} marked as ERROR after max attempts")
                        self.handle_errors(
                            error_description=f"Error occurred: attempt {tries} {e.message}",
                            send_sms="yes",
                            send_client_sms="yes" if tries == MAX_ATTEMPTS else "no",
                        )
                        try:
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
                            logging.warning(f"{self.__class__.__name__}: Close button not found after error on request {self.request.id}")
                            self.handle_errors(
                                error_description=f"After error: {e.message}",
                                send_sms="no",
                                send_client_sms="no",
                            )
                            self.driver.close()
                    except Exception as e:
                        tries = tries + 1
                        message = "Another type of exception occurred please check what happened"
                        complete_error_message = handle_general_exception(e, message)
                        logging.error(f"{self.__class__.__name__}: Unexpected exception on attempt {tries} for request {self.request.id}: {complete_error_message}", exc_info=True)
                        print(complete_error_message)
                        self.handle_errors(
                            error_description=complete_error_message,
                            send_sms="yes",
                            send_client_sms="no",
                        )
                        self.driver.close()
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Thread error while processing request: {e}", exc_info=True)
