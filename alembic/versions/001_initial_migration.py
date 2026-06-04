"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-06-04 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("phash", sa.Text, nullable=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("size", sa.BigInteger, nullable=True),
        sa.UniqueConstraint("path", "name", name="uq_images_path_name"),
    )
    op.create_index("ix_images_phash", "images", ["phash"])


def downgrade() -> None:
    op.drop_index("ix_images_phash", table_name="images")
    op.drop_table("images")