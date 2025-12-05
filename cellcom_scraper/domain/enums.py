from enum import Enum


class RequestType(str, Enum):
    ONT_PORT_IN_NUMBER = "ONT PORT IN NUMBER"
    ONT_SIM_EXTRACTION = "ONT SIM EXTRACTION"
    GTA_PORT_IN_NUMBER = "GTA PORT IN NUMBER"
    GTA_SIM_EXTRACTION = "GTA SIM EXTRACTION"
    PORT_IN_NUMBER = "PORT IN NUMBER"
    SIM_EXTRACTION = "SIM EXTRACTION"
    FICTIVE_NUMBER_PORT_IN = "FICTIVE NUMBER PORT IN"
    FICTIVE_NUMBER_SIM_EXTRACTION = "FICTIVE NUMBER SIM EXTRACTION"
    UPGRADE_STATUS_AND_DRO = "UPGRADE STATUS AND DRO"
    VIRGIN_UPGRADE_STATUS_AND_DRO = "VIRGIN UPGRADE STATUS AND DRO"


class RequestStatus(str, Enum):
    READY = "READY"
    FINISHED = "FINISHED"
    ERROR = "ERROR"
    IN_PROGRESS = "IN PROGRESS"


class ExecutionFrequency(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"


class ScraperControllerType(str, Enum):
    port_in_scraper = "port_in_scraper"
    upgrade_and_dro_scraper = "upgrade_and_dro_scraper"
