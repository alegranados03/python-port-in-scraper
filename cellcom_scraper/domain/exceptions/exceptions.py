import traceback


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
            f"Item was not found while executing scraper: {message}", "SEC001"
        )


class UnknownNavigatorException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Unknown navigator selected: {message}", "SEC005")


class UnknownStrategyException(ApplicationException):
    def __init__(self, message):
        super().__init__(f"Unknown strategy selected: {message}", "SEC006")
