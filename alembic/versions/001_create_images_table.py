import sqlalchemy as sa

from alembic import op


revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("phash", sa.String(length=32), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("size", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_images_phash", "images", ["phash"])
    op.create_index("ix_images_path_name", "images", ["path", "name"])


def downgrade() -> None:
    op.drop_index("ix_images_path_name")
    op.drop_index("ix_images_phash")
    op.drop_table("images")