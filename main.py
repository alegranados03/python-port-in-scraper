import logging
import os
from datetime import datetime

from cellcom_scraper.application.processor import Processor

from cellcom_scraper.domain.entities.account import AccountEntity
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork


class Main:
    def start(self):
        print(self.log_init_message())
        uow = DefaultUnitOfWork()
        credentials = self.get_credentials()
        processor = Processor(uow, credentials)
        try:
            processor.start_processor()
        except Exception as e:
            message = ""
            logging.error(message)
            logging.error(e)
            print(message)

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
        logging.basicConfig(filename="./scrapers.log", level=logging.DEBUG)
        # logging.info(init_message)
        return init_message
