from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")
K = TypeVar("K")


class Command(ABC, BaseModel):
    pass


class CommandHandler(ABC, Generic[T, K]):
    @abstractmethod
    def handle(self, command: T) -> K:
        raise NotImplementedError()


class Query(ABC, BaseModel):
    pass


class QueryHandler(ABC, Generic[T, K]):
    @abstractmethod
    def handle(self, query: T) -> K:
        raise NotImplementedError()
