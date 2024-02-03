from cellcom_scraper.config import FORCE_STOP_ERRORS, MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import ApplicationException
from cellcom_scraper.application.controllers.base_controller import BaseController

import logging


class PortInController(BaseController):
    def __init__(self) -> None:
        super().__init__()

    def execute(self, navigator_options=None) -> None:
        tries = 0
        while tries < MAX_ATTEMPTS:
            tries += 1
            self.builder.set_driver_options(options=navigator_options)
            self.builder.initialize_driver()
            self.strategy.set_driver(self.builder.get_driver())
            self.strategy.set_phone_number(self.phone_number)
            try:
                self.strategy.execute()
                self.handle_results()
                tries = MAX_ATTEMPTS + 1
            except ApplicationException as e:
                for error in FORCE_STOP_ERRORS:
                    if error in str(e):
                        tries = MAX_ATTEMPTS
                        break
                if tries == MAX_ATTEMPTS:
                    self.handle_error(
                        error_description=e.message,
                        send_sms="yes",
                        send_client_sms="yes",
                    )
                    raise ApplicationException("Scraper request failed", "E001")
                else:
                    self.handle_error(error_description=e.message, send_sms="no")
            except Exception as e:
                message = (
                    "Another type of exception occurred please check what happened"
                )
                self.handle_error(error_description=message, send_sms="yes")
                logging.error(e)
                logging.error(message)

        driver = self.builder.get_driver()
        driver.close()

    def handle_error(
        self, *, error_description, send_sms, send_client_sms="no", error_log=""
    ):
        screenshot: dict = self.strategy.take_screenshot()
        data: dict = {
            "error_description": error_description,
            "error_log": error_log,
            "result": "Fail",
            "process_id": self.aws_id,
            "error_filename": screenshot["filename"],
            "error_screenshot": screenshot["screenshot"],
            "send_sms": send_sms,
            "send_client_sms": send_client_sms,
        }
        endpoint: str = "report-errors"
        self.strategy.send_to_aws(data, endpoint)
