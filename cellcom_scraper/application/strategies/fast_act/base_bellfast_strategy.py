from cellcom_scraper.application.strategies.base_strategy import BaseScraperStrategy


class BellFastActBaseStrategy(BaseScraperStrategy):
    def __init__(self, credentials):
        super().__init__(credentials)
