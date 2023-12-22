from enum import Enum


class RequestType(str, Enum):
    PORT_IN_NUMBER = "PORT IN NUMBER"
    SIM_EXTRACTION = "SIM EXTRACTION"
    PORT_IN_VIA_FICTIVE_NUMBER = "PORT INT VIA FICTIVE NUMBER"


class RequestStatus(str, Enum):
    READY = "READY"
    FINISHED = "FINISHED"
    ERROR = "ERROR"
