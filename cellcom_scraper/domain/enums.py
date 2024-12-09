from enum import Enum


class RequestType(str, Enum):
    PORT_IN_NUMBER = "PORT IN NUMBER"
    SIM_EXTRACTION = "SIM EXTRACTION"
    FICTIVE_NUMBER_PORT_IN = "FICTIVE NUMBER PORT IN"
    FICTIVE_NUMBER_SIM_EXTRACTION = "FICTIVE NUMBER SIM EXTRACTION"
    UPGRADE_STATUS_AND_DRO = "UPGRADE STATUS AND DRO"
    VIRGIN_UPGRADE_STATUS_AND_DRO = "VIRGIN STATUS AND DRO"


class RequestStatus(str, Enum):
    READY = "READY"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class ExecutionFrequency(str, Enum):
    ONCE: str = "ONCE"
    DAILY: str = "DAILY"
    MONTHLY: str = "MONTHLY"


class ScraperControllerType(str, Enum):
    port_in_scraper: str = "port_in_scraper"
    upgrade_and_dro_scraper: str = "upgrade_and_dro_scraper"
