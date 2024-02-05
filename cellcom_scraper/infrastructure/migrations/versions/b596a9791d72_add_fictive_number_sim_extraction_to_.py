"""add fictive number sim extraction to types

Revision ID: b596a9791d72
Revises: e05989884033
Create Date: 2023-12-29 08:40:29.625279

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b596a9791d72'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '662d8c8df97d'


def upgrade() -> None:
    op.execute(
        "ALTER TABLE process_queue MODIFY COLUMN type ENUM('PORT IN NUMBER', 'SIM EXTRACTION', 'FICTIVE NUMBER PORT IN', 'FICTIVE NUMBER SIM EXTRACTION')"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE process_queue MODIFY COLUMN type ENUM('PORT IN NUMBER', 'SIM EXTRACTION', 'FICTIVE NUMBER PORT IN')"
    )
