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
            self.request = self.uow.get_repository(
                "process_requests"
            ).filter_with_skip_locked(
                limit=1,
                status=RequestStatus.READY.value,
                scraper_id=1,
            )
        except Exception as e:
            print(
                handle_general_exception(
                    e, "Requests fetch on Port In Controller failed"
                )
            )
            logging.error(f"Requests fetch on {self.__class__.__name__} failed")

    def execute(self):
        while True:
            with self.uow:
                try:
                    transaction = self.uow.session.begin()
                    self._get_request()
                    if not self.request:
                        break
                    self._update_request_status(
                        request=self.request, status=RequestStatus.IN_PROGRESS
                    )
                    transaction.commit()
                except Exception as e:
                    logging.error("Error occurred on request transaction")
                    logging.error(f"PortInController: Thread error: {e}")
                    transaction.close()

            try:
                request_type: RequestType = RequestType(self.request.type)
                self.set_strategy(request_type)
                self.strategy.set_phone_number(self.request.number_to_port)
                self.strategy.set_aws_id(self.request.aws_id)
                tries = 0
                while tries < MAX_ATTEMPTS:
                    try:
                        self.set_environment()
                        self.strategy.set_driver(self.builder.get_driver())
                        self.strategy.execute()
                        self.handle_results()
                        tries = MAX_ATTEMPTS + 1
                        self._update_request_status(
                            request=self.request, status=RequestStatus.FINISHED
                        )
                        try:
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
                            self.handle_errors(
                                error_description=e.message,
                                send_sms="yes",
                                send_client_sms="no",
                            )
                            self.driver.close()
                    except ApplicationException as e:
                        tries = tries + 1
                        for error in FORCE_STOP_ERRORS:
                            if error in str(e):
                                tries = MAX_ATTEMPTS
                        if tries == MAX_ATTEMPTS:
                            self._update_request_status(
                                request=self.request, status=RequestStatus.ERROR
                            )
                        self.handle_errors(
                            error_description=f"Error occurred: attempt {tries} {e.message}",
                            send_sms="yes",
                            send_client_sms="yes" if tries == MAX_ATTEMPTS else "no",
                        )
                        try:
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
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
                        print(complete_error_message)
                        self.handle_errors(
                            error_description=complete_error_message,
                            send_sms="yes",
                            send_client_sms="no",
                        )
                        self.driver.close()
            except Exception as e:
                logging.error(f"PortInController: Thread error: {e}")
