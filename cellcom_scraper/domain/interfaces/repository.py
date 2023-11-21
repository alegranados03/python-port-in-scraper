from abc import ABC, abstractmethod
from typing import Any, TypeVar

Entity = TypeVar("Entity")
Model = TypeVar("Model")


class Repository(ABC):
    """Abstract class that represents a database repository."""

    @abstractmethod
    def create(self, entity: Entity) -> Model:
        raise NotImplementedError

    @abstractmethod
    def update(self, id_: int, entity: Entity) -> Model:
        raise NotImplementedError

    @abstractmethod
    def get(self, id_: int) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id_: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_all_by_filter(self, **filters) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_one_by_filter(self, **filters) -> None:
        raise NotImplementedError

    @abstractmethod
    def filter_by(self, **filters) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    def get_by_filter(self, **filters) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def filter(self, **filters) -> list[Entity]:
        raise NotImplementedError
