from enum import Enum


class RequestType(str, Enum):
    PORT_IN_NUMBER = "PORT IN NUMBER"
    SIM_EXTRACTION = "SIM EXTRACTION"


class RequestStatus(str, Enum):
    READY = "READY"
    IN_PROGRESS = "IN PROGRESS"
    FINISHED = "FINISHED"
    ERROR = "ERROR"
