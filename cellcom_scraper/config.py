import os

MAX_ATTEMPTS = 10
UPGRADE_AND_DRO_MAX_ATTEMPTS = 3
FORCE_STOP_ERRORS = [
    "SIM number not found",
    "No subscriber found",
    "Phone number not found",
    "The original order cannot be found for this port-in number. Please verify the information entered and try again.",
    "The status for the mobile number entered is not valid.",
    "The number entered does not meet the criteria for port-in date change.",
    "The Port in Date change function is not available for previous mobile number change transactions. Please contact Retail Support to complete the transaction.",
    "A Port In request is still in progress and changes cannot be made at this time. Please contact Retail Support to complete the request.",
    "There is currently a future dated transaction on this account. Please call Bell Mobility.",
    "For interbrand transfers, please complete an Account Migration transaction through fastACT.",
    "Unknown fictive number port in configuration",
    "Only accounts with Open or Suspended status can be viewed",
    "A port request is already in progress. Go to Order Search to retrieve and continue with the original order.",
]
PORT_IN_AWS_SERVER = os.environ.get("PORT_IN_AWS_SERVER")
UPGRADE_AND_DRO_AWS_SERVER = os.environ.get("UPGRADE_AND_DRO_AWS_SERVER")
