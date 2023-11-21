import datetime
from abc import abstractmethod
from typing import Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from cellcom_scraper.domain.interfaces.repository import Repository
from cellcom_scraper.infrastructure.sqlalchemy.models import Base

Entity = TypeVar("Entity", bound=BaseModel)
Model = TypeVar("Model", bound=Base)


class SQLAlchemyRepository(Repository):
    class Meta:
        model = None

    def __init__(self, session: Session) -> None:
        super(SQLAlchemyRepository, self).__init__()
        self.session: Session = session

    def get_model(self) -> Model:
        return self.Meta.model

    @abstractmethod
    def to_orm_model(self, entity: Entity) -> Model:
        raise NotImplementedError()

    def get(self, id_: int) -> Entity:
        result = self.session.query(self.get_model()).get(id_)
        if not result:
            raise Exception
        return result.to_entity()

    def create(self, entity: Entity) -> Model:
        result: Model = self.get_model()(**entity.model_dump())
        self.session.add(result)
        return result

    def update(self, id_: int, entity: Entity) -> Model:
        result: Model = self.session.query(self.get_model()).get(id_)
        if not result:
            raise Exception
        for key, value in entity.model_dump().items():
            if hasattr(result, key):
                setattr(result, key, value)
        return result

    def delete(self, id_: int) -> None:
        result = self.session.query(self.get_model()).get(id_)
        if not result:
            raise Exception
        self.session.delete(result)

    def delete_all_by_filter(self, **filters) -> None:
        results = self.session.query(self.get_model()).filter_by(**filters).all()
        for result in results:
            self.session.delete(result)

    def delete_one_by_filter(self, **filters) -> None:
        results = self.session.query(self.get_model()).filter_by(**filters).all()
        if len(results) == 0:
            raise Exception
        self.session.delete(results[0])

    def filter_by(self, **filters) -> list[Entity]:
        results = self.session.query(self.get_model()).filter_by(**filters).all()
        return [record.to_entity() for record in results]

    def get_by_filter(self, **filters) -> Optional[list[Entity]]:
        results = self.session.query(self.get_model()).filter_by(**filters).all()
        if len(results) == 0:
            return None
        return results[0].to_entity()

    def filter(self, **filters) -> list[Entity]:
        context = {self.get_model().__name__: self.get_model(), "datetime": datetime}
        results = (
            self.session.query(self.get_model())
            .filter(
                *[eval(filter_, context) for filter_ in self.format_filters(**filters)]
            )
            .all()
        )
        return [record.to_entity() for record in results]

    def format_filters(self, **filters) -> list[str]:
        operators = {
            "lt": "<",
            "lte": "<=",
            "gt": ">",
            "gte": ">=",
            "eq": "==",
            "ne": "!=",
        }
        mapped_filters: list[str] = []
        for filter_, value in filters.items():
            attr_operation: list[str] = filter_.split("__")
            if len(attr_operation) == 1:
                mapped_filters.append(
                    f"{self.get_model().__name__}.{attr_operation[0]} == {repr(value)}"
                )
            elif len(attr_operation) >= 2:
                operator_str = operators.get(attr_operation[-1], "==")
                field_name = ".".join(attr_operation[:-1])
                mapped_filters.append(
                    f"{self.get_model().__name__}.{field_name} {operator_str} {repr(value)}"
                )
        return mapped_filters
