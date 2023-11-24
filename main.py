import logging
from datetime import datetime

from cellcom_scraper.application.processor import Processor
from cellcom_scraper.application.scrapers.scraper_controller import ScraperController
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from cellcom_scraper.domain.entities.account import AccountEntity
import os


current_date = datetime.now()
logging.basicConfig(filename="./scrapers.log", level=logging.DEBUG)
logging.info(f"Port in Scraper, execution start at: {current_date}")


class Main:
    def start(self):
        uow = DefaultUnitOfWork()
        controller = ScraperController()
        credentials = self.get_credentials()
        processor = Processor(uow, controller, credentials)
        with uow:
            processor.set_requests(
                uow.get_repository("process_requests").filter(status="READY")
            )
        processor.start_processor()

    @staticmethod
    def get_credentials():
        return AccountEntity(
            username=os.getenv("BELL_FAST_USERNAME"),
            dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
            password=os.getenv("BELL_FAST_PASSWORD"),
        )
