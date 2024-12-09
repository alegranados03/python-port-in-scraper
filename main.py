import logging
import os
import traceback
from datetime import datetime

from cellcom_scraper.application.processor import Processor
from cellcom_scraper.domain.entities.account import AccountEntity
from cellcom_scraper.domain.exceptions import ApplicationException
from cellcom_scraper.domain.exceptions.exceptions import handle_general_exception


class Main:
    def start(self):
        print(self.log_init_message())
        processor = Processor()
        try:
            processor.start_processor()
        except ApplicationException as e:
            logging.error(e.message)
            print(e.message)
        except Exception as e:
            message = "Another type of exception occurred at start"
            print(handle_general_exception(e, message))


    @staticmethod
    def log_init_message():
        current_date = datetime.now()
        init_message = f"Scraper requests processor, execution start at: {current_date}"
        logging.basicConfig(filename="./scrapers.log", level=logging.WARNING)
        # logging.info(init_message)
        return init_message


main = Main()
main.start()
