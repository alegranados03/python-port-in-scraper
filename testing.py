from datetime import datetime
from enum import Enum

from pydantic import BaseModel

CREATE_RECONCILIATION_CONTROL_TABLE_SQL: str = "CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER AUTOINCREMENT PRIMARY KEY,{columns})"


class ReconciliationSide(str, Enum):
    A: str = "A"
    B: str = "B"


class ReconciliationStatus(str, Enum):
    TO_BE_EXECUTED: str = "To be executed"
    PROCESSED: str = "Processed"
    EMPTY: str = "Empty"
    FAILED: str = "Failed"
    REMOVED: str = "Removed"


class ReconciliationKPI(BaseModel):
    resource_id: int
    reconciliation_id: int
    reconciliation_name: str
    side: ReconciliationSide
    position: int
    status: ReconciliationStatus
    date_last_updated: datetime
    total_records: float
    reconciled_records: float
    adjusted_records: float
    unreconciled_records: float
    reconciled_records_percentage: float
    adjusted_records_percentage: float
    unreconciled_records_percentage: float
    total_amount: float
    reconciled_amount: float
    adjusted_amount: float
    unreconciled_amount: float
    reconciled_amount_percentage: float
    adjusted_amount_percentage: float
    unreconciled_amount_percentage: float


class HistoricalReconciliationKPI(ReconciliationKPI):
    created_at: datetime


class ReconciliationKPIDetails(BaseModel):
    side: ReconciliationSide
    total_records: float
    reconciled_records: float
    adjusted_records: float
    unreconciled_records: float
    reconciled_records_percentage: float
    adjusted_records_percentage: float
    unreconciled_records_percentage: float
    total_amount: float
    reconciled_amount: float
    adjusted_amount: float
    unreconciled_amount: float
    reconciled_amount_percentage: float
    adjusted_amount_percentage: float
    unreconciled_amount_percentage: float


class GeneralsReconciliationKPI(BaseModel):
    resource_id: int
    reconciliation_id: int
    reconciliation_name: str
    position: int
    status: ReconciliationStatus
    date_last_updated: datetime


class CombinedReconciliationKPI(GeneralsReconciliationKPI):
    details: list[ReconciliationKPIDetails]


data = [
    {
        "resource_id": 3,
        "reconciliation_id": 7,
        "reconciliation_name": "Reconciliation 88",
        "side": "A",
        "position": 7,
        "status": "To be executed",
        "date_last_updated": datetime(2023, 11, 15, 15, 28, 5, 124072),
        "total_records": 1111,
        "reconciled_records": 333.46,
        "adjusted_records": 52.16,
        "unreconciled_records": 27.76,
        "reconciled_records_percentage": 1.05,
        "adjusted_records_percentage": 30.95,
        "unreconciled_records_percentage": 1.34,
        "total_amount": 4835.72,
        "reconciled_amount": 3328.16,
        "adjusted_amount": 763.61,
        "unreconciled_amount": 1086.83,
        "reconciled_amount_percentage": 64.22,
        "adjusted_amount_percentage": 73.26,
        "unreconciled_amount_percentage": 88.58,
    },
    {
        "resource_id": 3,
        "reconciliation_id": 7,
        "reconciliation_name": "Reconciliation 88",
        "side": "B",
        "position": 7,
        "status": "To be executed",
        "date_last_updated": datetime(2023, 11, 15, 15, 28, 5, 124072),
        "total_records": 267,
        "reconciled_records": 333.46,
        "adjusted_records": 52.16,
        "unreconciled_records": 27.76,
        "reconciled_records_percentage": 31.05,
        "adjusted_records_percentage": 344.95,
        "unreconciled_records_percentage": 1.34,
        "total_amount": 455.72,
        "reconciled_amount": 3328.16,
        "adjusted_amount": 763.62,
        "unreconciled_amount": 1686.83,
        "reconciled_amount_percentage": 64.22,
        "adjusted_amount_percentage": 21.26,
        "unreconciled_amount_percentage": 89.58,
    },
    {
        "resource_id": 84,
        "reconciliation_id": 15,
        "reconciliation_name": "Reconciliation 94",
        "side": "A",
        "position": 1,
        "status": "To be executed",
        "date_last_updated": datetime(2023, 12, 6, 15, 28, 5, 124305),
        "total_records": 255.29,
        "reconciled_records": 327.49,
        "adjusted_records": 68.55,
        "unreconciled_records": 74.00,
        "reconciled_records_percentage": 23.29,
        "adjusted_records_percentage": 866.88,
        "unreconciled_records_percentage": 70.08,
        "total_amount": 51238.35,
        "reconciled_amount": 555.71,
        "adjusted_amount": 666.67,
        "unreconciled_amount": 1379.82,
        "reconciled_amount_percentage": 64.10,
        "adjusted_amount_percentage": 48.81,
        "unreconciled_amount_percentage": 82.94,
    },
    {
        "resource_id": 84,
        "reconciliation_id": 15,
        "reconciliation_name": "Reconciliation 94",
        "side": "B",
        "position": 1,
        "status": "To be executed",
        "date_last_updated": datetime(2023, 12, 6, 15, 28, 5, 124305),
        "total_records": 257.29,
        "reconciled_records": 377.49,
        "adjusted_records": 68.55,
        "unreconciled_records": 77.00,
        "reconciled_records_percentage": 23.29,
        "adjusted_records_percentage": 8.88,
        "unreconciled_records_percentage": 90.08,
        "total_amount": 5498.35,
        "reconciled_amount": 4182.71,
        "adjusted_amount": 354.67,
        "unreconciled_amount": 1379.81,
        "reconciled_amount_percentage": 64.80,
        "adjusted_amount_percentage": 98.81,
        "unreconciled_amount_percentage": 82.98,
    },
]


results = [ReconciliationKPI(**d) for d in data]
details_to_exclude = set(ReconciliationKPIDetails.__annotations__.keys())
general_to_exclude = set(GeneralsReconciliationKPI.__annotations__.keys())
merged_kpis = {}
for result in results:
    if result.resource_id not in merged_kpis:
        merged_kpis[result.resource_id] = {
            **result.dict(exclude=details_to_exclude),
            "details": [],
        }
    merged_kpis[result.resource_id]["details"].append(
        result.dict(exclude=general_to_exclude)
    )

final = []
for merged in merged_kpis.values():
    kpi_details = [ReconciliationKPIDetails(**detail) for detail in merged["details"]]
    combined_kpis = CombinedReconciliationKPI(
        resource_id=merged["resource_id"],
        reconciliation_id=merged["reconciliation_id"],
        reconciliation_name=merged["reconciliation_name"],
        position=merged["position"],
        status=merged["status"],
        date_last_updated=merged["date_last_updated"],
        details=kpi_details,
    )
    final.append(combined_kpis)
