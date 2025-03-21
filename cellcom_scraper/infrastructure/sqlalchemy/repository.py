import datetime
from abc import abstractmethod
from typing import Optional, TypeVar, Union

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
        results = self._filter_query(**filters).all()
        return [record.to_entity() for record in results]

    def _filter_query(self, **filters):
        context = {self.get_model().__name__: self.get_model(), "datetime": datetime}
        return (
            self.session.query(self.get_model())
            .filter(
                *[eval(filter_, context) for filter_ in self.format_filters(**filters)]
            )
        )

    def filter_with_skip_locked(self, limit=1, **filters) -> Entity | None:
        result = self._filter_query(**filters).limit(limit).with_for_update(skip_locked=True).first()
        if result:
            return result.to_entity()

    def format_filters(self, **filters) -> list[str]:
        operators = {
            "lt": "<",
            "lte": "<=",
            "gt": ">",
            "gte": ">=",
            "eq": "==",
            "ne": "!=",
            "in": "in",
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
                if operator_str == "in":
                    value_list = ", ".join(repr(v) for v in value)
                    mapped_filters.append(
                        f"{self.get_model().__name__}.{field_name} {operator_str} ({value_list})"
                    )
                else:
                    mapped_filters.append(
                        f"{self.get_model().__name__}.{field_name} {operator_str} {repr(value)}"
                    )
        return mapped_filters
