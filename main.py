import logging
from datetime import datetime, timedelta

from cellcom_scraper.application.processor import Processor
from cellcom_scraper.application.scrapers.scraper_controller import ScraperController
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork

current_date = datetime.now()
logging.basicConfig(filename="./scrapers.log", level=logging.DEBUG)
logging.info(f"Port in Scraper, execution start at: {current_date}")


class Main:
    @staticmethod
    def start():
        uow = DefaultUnitOfWork()
        controller = ScraperController()
        processor = Processor(uow, controller)
        with uow:
            processor.set_requests(
                uow.get_repository("process_requests").filter(status="READY")
            )
        processor.start_processor()
