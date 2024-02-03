"""scraper table seeder

Revision ID: 884b60daddf3
Revises: 459c59f80552
Create Date: 2024-02-03 08:05:05.311413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

from alembic import op
from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision: str = '884b60daddf3'
down_revision: Union[str, None] = '459c59f80552'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    scraper_table = table(
        "scrapers",
        column("id", Integer),
        column("name", String),
        column("url", String),
        column("slug", String),
        column("execution_frequency", Enum("ONCE", "DAILY", "MONTHLY")),
        column("available", Boolean),
    )
    op.bulk_insert(
        scraper_table,
        [
            {
                "id": 1,
                "name": "Port in Scraper",
                "url": "https://wac.bell.ca:8000/wac-ia/bell_login.jsp",
                "slug": "port_in_scraper",
                "execution_frequency": "ONCE",
                "available": True,
            },
            {
                "id": 2,
                "name": "Upgrade and DRO Scraper",
                "url": "https://wac.bell.ca:8000/wac-ia/bell_login.jsp",
                "slug": "upgrade_and_dto_scraper",
                "execution_frequency": "ONCE",
                "available": True,
            },
        ],
    )


def downgrade() -> None:
    pass
