from enum import Enum


class RequestType(str, Enum):
    PORT_IN_NUMBER = "PORT IN NUMBER"
    SIM_EXTRACTION = "SIM EXTRACTION"
    FICTIVE_NUMBER_PORT_IN = "FICTIVE NUMBER PORT IN"
    FICTIVE_NUMBER_SIM_EXTRACTION = "FICTIVE NUMBER SIM EXTRACTION"


class RequestStatus(str, Enum):
    READY = "READY"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class ExecutionFrequency(str, Enum):
    ONCE: str = "ONCE"
    DAILY: str = "DAILY"
    MONTHLY: str = "MONTHLY"
