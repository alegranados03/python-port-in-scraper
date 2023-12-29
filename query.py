from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, IntEnum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")
K = TypeVar("K")


class Query(ABC, BaseModel):
    pass


class QueryHandler(ABC, Generic[T, K]):
    @abstractmethod
    def handle(self, query: T) -> K:
        raise NotImplementedError()  # pragma: nocover


class ReconciliationSide(str, Enum):
    A: str = "A"
    B: str = "B"


class ReconciliationStatus(str, Enum):
    TO_BE_EXECUTED: str = "To be executed"
    PROCESSED: str = "Processed"
    EMPTY: str = "Empty"
    FAILED: str = "Failed"
    REMOVED: str = "Removed"


class OrderEnum(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ReconciliationControlOrderByFilters(BaseModel):
    date_last_updated: Optional[OrderEnum] = None
    total_records: Optional[OrderEnum] = None
    reconciled_records: Optional[OrderEnum] = None
    adjusted_records: Optional[OrderEnum] = None
    unreconciled_records: Optional[OrderEnum] = None
    reconciled_records_percentage: Optional[OrderEnum] = None
    adjusted_records_percentage: Optional[OrderEnum] = None
    unreconciled_records_percentage: Optional[OrderEnum] = None
    total_amount: Optional[OrderEnum] = None
    reconciled_amount: Optional[OrderEnum] = None
    adjusted_amount: Optional[OrderEnum] = None
    unreconciled_amount: Optional[OrderEnum] = None
    reconciled_amount_percentage: Optional[OrderEnum] = None
    adjusted_amount_percentage: Optional[OrderEnum] = None
    unreconciled_amount_percentage: Optional[OrderEnum] = None


class ReconciliationControlFilters(BaseModel):
    side: Optional[ReconciliationSide] = None
    status__in: Optional[list[ReconciliationStatus]] = None
    reconciliation_name: Optional[str] = Field(None, pattern="^[^'%/:@!$&*()=]+$")


class GetReconciliationControlFiltersSQLQuery(Query):
    filters: Optional[dict]


class GetReconciliationControlFiltersSQLQueryHandler(
    QueryHandler[GetReconciliationControlFiltersSQLQuery, tuple[str, str, dict]]
):
    def __init__(self) -> None:
        self.params: dict = {}

    def handle(
        self, query: GetReconciliationControlFiltersSQLQuery
    ) -> tuple[str, str, dict]:
        if query.filters:
            if "status__in" in query.filters:
                query.filters["status__in"] = query.filters["status__in"].split(",")
            filters: ReconciliationControlFilters = ReconciliationControlFilters(
                **query.filters
            )
            order_by_filters: ReconciliationControlOrderByFilters = (
                ReconciliationControlOrderByFilters(**query.filters)
            )
            where: str = self.build_where_sentence(filters=filters)
            order: str = self.build_order_by_sentence(filters=order_by_filters)
            return where, order, self.params
        return "", "", self.params

    def build_where_sentence(self, filters: ReconciliationControlFilters) -> str:
        conditions: list = []
        if filters.side:
            conditions.append("SIDE=%(side)s")
            self.params["side"] = f"{filters.side.value}"

        if filters.status__in:
            conditions.append("STATUS IN (%(status)s)")
            self.params["status"] = ", ".join(
                [f"{s.value}" for s in filters.status__in]
            )

        if filters.reconciliation_name:
            conditions.append("RECONCILIATION_NAME ILIKE %(name)s")
            self.params["name"] = f"%{filters.reconciliation_name}%"

        conditions_string = " AND ".join(conditions)
        query = f"WHERE {conditions_string}" if conditions else ""
        return query

    def build_order_by_sentence(
        self, filters: ReconciliationControlOrderByFilters
    ) -> str:
        conditions: list = []
        for filter, order_type in filters.dict().items():
            if order_type:
                conditions.append(f"{filter.upper()} {order_type.value}")
                self.params[filter] = order_type.value

        conditions_string = ", ".join(conditions)
        query = f"ORDER BY {conditions_string}" if conditions else ""
        return query % self.params


query_params = {
    "side": "B",
    "status__in": "Empty,Processed",
    # "reconciliation_name" : "",
    "date_last_updated": "DESC",
    "total_records": "ASC",
    "reconciled_records": "DESC",
    "adjusted_records": "ASC",
    "unreconciled_records": "DESC",
    "reconciled_records_percentage": "ASC",
    "adjusted_records_percentage": "DESC",
    "unreconciled_records_percentage": "ASC",
    "total_amount": "DESC",
    "reconciled_amount": "ASC",
    "adjusted_amount": "DESC",
    "unreconciled_amount": "ASC",
    "reconciled_amount_percentage": "DESC",
    "adjusted_amount_percentage": "ASC",
    "unreconciled_amount_percentage": "DESC",
}

query = GetReconciliationControlFiltersSQLQuery(filters=query_params)
where, order, params = GetReconciliationControlFiltersSQLQueryHandler().handle(
    query=query
)
# print(order)
[f for f in ReconciliationControlOrderByFilters.model_fields.keys()]


print(
    ReconciliationControlOrderByFilters(**query_params).dict(
        exclude={"date_last_updated"}
    )
)
