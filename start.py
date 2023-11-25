from dotenv import load_dotenv

load_dotenv()
import time

import schedule

from main import Main


def fetch():
    main_app = Main()
    main_app.start()


if __name__ == "__main__":
    schedule.every(10).seconds.do(fetch)

    while True:
        schedule.run_pending()
        time.sleep(1)
