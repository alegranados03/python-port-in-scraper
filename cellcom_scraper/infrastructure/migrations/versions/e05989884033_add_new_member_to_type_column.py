"""add new member to type column

Revision ID: e05989884033
Revises: 662d8c8df97d
Create Date: 2023-12-23 09:10:41.627186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e05989884033"
down_revision: Union[str, None] = "662d8c8df97d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE process_queue MODIFY COLUMN type ENUM('PORT IN NUMBER', 'SIM EXTRACTION', 'FICTIVE NUMBER PORT IN')"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE process_queue MODIFY COLUMN type ENUM('PORT IN NUMBER', 'SIM EXTRACTION')"
    )
