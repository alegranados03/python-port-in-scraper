from cellcom_scraper.config import FORCE_STOP_ERRORS, UPGRADE_AND_DRO_MAX_ATTEMPTS
from cellcom_scraper.domain.exceptions import ApplicationException
from cellcom_scraper.application.controllers.base_controller import BaseController

import traceback
import logging

class UpgradeAndDroController(BaseController):
    def __init__(self) -> None:
        super().__init__()

    def execute(self, navigator_options=None) -> None:
        tries = 0
        while tries < UPGRADE_AND_DRO_MAX_ATTEMPTS:
            tries += 1
            self.builder.set_driver_options(options=navigator_options)
            self.builder.initialize_driver()
            self.strategy.set_driver(self.builder.get_driver())
            self.strategy.set_phone_number(self.phone_number)
            try:
                self.strategy.execute()
                self.handle_results()
                tries = UPGRADE_AND_DRO_MAX_ATTEMPTS + 1
            except ApplicationException as e:
                for error in FORCE_STOP_ERRORS:
                    if error in str(e):
                        tries = UPGRADE_AND_DRO_MAX_ATTEMPTS
                        break
                if tries == UPGRADE_AND_DRO_MAX_ATTEMPTS:
                    message = "Scraper request failed, max attempts reached"
                    self.handle_error(aws_id=self.aws_id, description=message)
                    raise ApplicationException(message, "E001")
                else:
                    message = f"attempt {tries} failed {e.message}"
                    self.handle_error(aws_id=self.aws_id, description=message)
            except Exception as e:
                error_message = str(e)
                error_type = type(e).__name__
                error_traceback = traceback.format_exc()
                full_error_message = (
                    f"Exception Type:"
                    f"{error_type}\nMessage: {error_message}\nTraceback:\n{error_traceback}"
                )
                message = "Unknown error occurred, please notify this error to the administrator"
                logging.error(message)
                logging.error(full_error_message)
                self.handle_error(
                    aws_id=self.aws_id, description=message, details=full_error_message
                )

        driver = self.builder.get_driver()
        driver.close()

    def handle_error(self, *, aws_id: int, description: str, details=""):
        screenshot: dict = self.strategy.take_screenshot()
        payload = {
            "description": description,
            "screenshot": screenshot["screenshot"],
            "details": details,
        }
        endpoint: str = f"phones/{aws_id}/logs/error"
        self.strategy.send_to_aws(data=payload, endpoint=endpoint)
