import time

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

    def _get_requests(self) -> None:
        try:
            with self.uow:
                self.requests = self.uow.get_repository("process_requests").filter(
                    status="READY", scraper_id=1
                )
        except Exception as e:
            print(
                handle_general_exception(
                    e, "Requests fetch on Port In Controller failed"
                )
            )

    def execute(self):
        self._get_requests()
        while self.requests:
            for request in self.requests:
                self.set_environment()
                request_type: RequestType = RequestType(request.type)
                self.set_strategy(request_type)
                self.strategy.set_driver(self.builder.get_driver())
                self.strategy.set_phone_number(request.number_to_port)
                self.strategy.set_aws_id(request.aws_id)
                tries = 0
                while tries < MAX_ATTEMPTS:
                    try:
                        self.strategy.execute()
                        self.handle_results()
                        tries = MAX_ATTEMPTS + 1
                        self._update_request_status(
                            request=request, status=RequestStatus.FINISHED
                        )
                        if self.webdriver_is_active():
                            self.click_screen_close_button()
                    except CloseButtonNotFoundException as e:
                        self.handle_errors(
                            error_description=e.message,
                            send_sms="no",
                            send_client_sms="no",
                        )
                        self.driver.close()
                    except ApplicationException as e:
                        tries = tries + 1
                        for error in FORCE_STOP_ERRORS:
                            if error in str(e):
                                tries = MAX_ATTEMPTS
                                break
                        if tries == MAX_ATTEMPTS:
                            self._update_request_status(
                                request=request, status=RequestStatus.ERROR
                            )
                            self.handle_errors(
                                error_description=e.message,
                                send_sms="yes",
                                send_client_sms="yes",
                            )
                        try:
                            if self.webdriver_is_active():
                                self.click_screen_close_button()
                        except CloseButtonNotFoundException as e:
                            self.handle_errors(
                                error_description=e.message,
                                send_sms="no",
                                send_client_sms="no",
                            )
                            self.driver.close()
                    except Exception as e:
                        tries = tries + 1
                        message = "Another type of exception occurred please check what happened"
                        print(handle_general_exception(e, message))
                        self.driver.close()
                    

            time.sleep(60)
            self._get_requests()
