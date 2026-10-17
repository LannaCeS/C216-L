"""prevent duplicate names ignoring case and surrounding spaces

Revision ID: 0002_normalize_alunos_name
Revises: 0001_create_alunos
Create Date: 2026-10-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_normalize_alunos_name"
down_revision: str | None = "0001_create_alunos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_alunos_normalized_name",
        "alunos",
        [sa.text("lower(trim(name))")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_alunos_normalized_name", table_name="alunos")
