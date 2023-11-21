from abc import ABC, abstractmethod

from cellcom_scraper.domain.interfaces.repository import Repository


class UnitOfWork(ABC):
    """Abstract unit of work."""

    def __enter__(self) -> "UnitOfWork":
        """Context manager method for the UnitOfWork setup phase.

        Returns:
            UnitOfWork: The unit of work instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager method when encountering an Exception using the UnitOfWork in teardown phase."""
        self.rollback()

    @abstractmethod
    def flush(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    def get_repository(self, name: str) -> Repository:
        return getattr(self, name.lower())
