import logging
import os
import traceback
from datetime import datetime

from cellcom_scraper.application.processor import Processor
from cellcom_scraper.domain.entities.account import AccountEntity
from cellcom_scraper.domain.exceptions import ApplicationException
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception


class Main:
    def start(self):
        print(self.log_init_message())
        uow = DefaultUnitOfWork()
        credentials = self.get_credentials()
        processor = Processor(uow, credentials)
        try:
            processor.start_processor()
        except ApplicationException as e:
            logging.error(e.message)
            print(e.message)
        except Exception as e:
            message = "Another type of exception occurred at start"
            print(handle_general_exception(e, message))

    @staticmethod
    def get_credentials():
        return AccountEntity(
            username=os.getenv("BELL_FAST_USERNAME"),
            dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
            password=os.getenv("BELL_FAST_PASSWORD"),
        )

    @staticmethod
    def log_init_message():
        current_date = datetime.now()
        init_message = f"Scraper requests processor, execution start at: {current_date}"
        logging.basicConfig(filename="./scrapers.log", level=logging.WARNING)
        # logging.info(init_message)
        return init_message


main = Main()
main.start()
