import os

MAX_ATTEMPTS = 10
FORCE_STOP_ERRORS = [
    "SIM number not found",
    "Phone number not found",
    "The original order cannot be found for this port-in number. Please verify the information entered and try again.",
    "The status for the mobile number entered is not valid.",
    "The number entered does not meet the criteria for port-in date change.",
    "The Port in Date change function is not available for previous mobile number change transactions. Please contact Retail Support to complete the transaction.",
    "A Port In request is still in progress and changes cannot be made at this time. Please contact Retail Support to complete the request.",
]
AWS_SERVER_URL = os.environ.get("AWS_SERVER_URL")
