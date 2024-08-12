import traceback
import logging


class ApplicationException(Exception):
    def __init__(self, message: str, code: str, *, extra=None) -> None:
        super().__init__(message)
        self.message: str = message
        self.code: str = code
        self.extra = extra
        self.traceback = traceback.format_exc()


class NoItemFoundException(ApplicationException):
    def __init__(self, message):
        super().__init__(
            f"Item was not found while executing scraper: {message}", "SEC007"
        )


class SimExtractionException(ApplicationException):
    def __init__(self, message):
        super().__init__(message, "SEC002")


class PortInNumberException(ApplicationException):
    def __init__(self, message):
        super().__init__(message, "SEC003")


class ForcedStopException(ApplicationException):
    def __init__(self, message):
        super().__init__(message, "SEC004")


class UnknownNavigatorException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Unknown navigator selected: {message}", "SEC005")


class UnknownStrategyException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Unknown strategy selected: {message}", "SEC006")


class UnknownConfigurationException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Unknown configuration selected: {message}", "SEC008")


class UnknownFictiveNumberPortInException(ApplicationException):
    def __init__(self, message):
        super().__init__(
            f"Unknown fictive number port in configuration: {message}", "SEC009"
        )


class UnknownControllerException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Unknown controller: {message}", "SEC010")


class CloseButtonNotFoundException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Can't close process {message}", "SEC011")


def handle_general_exception(exception: Exception, message: str) -> str:
    error_message = str(exception)
    error_type = type(exception).__name__
    error_traceback = traceback.format_exc()
    full_error_message = (
        f"Exception Type:"
        f"{error_type}\n Message: {error_message}\n Traceback:\n{error_traceback}"
    )
    logging.error(full_error_message)
    logging.error(message)
    return message + full_error_message


class UpgradeStatusException(ApplicationException):
    def __init__(self, message):
        super().__init__(message, "SEC0012")


class LoginFailedException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Login failed: {message}", "SEC012")
