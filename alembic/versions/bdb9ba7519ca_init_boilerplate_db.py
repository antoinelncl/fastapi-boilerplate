"""init boilerplate db

Revision ID: bdb9ba7519ca
Revises:
Create Date: 2024-07-03 11:03:37.252416

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bdb9ba7519ca"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            default=sa.func.now(),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "email_tokens",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("token", sa.String(255), nullable=False, unique=True),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index(op.f("ix_email_token_token"), "email_tokens", ["token"], unique=True)
    op.create_foreign_key("fk_email_token_user_id_users", "email_tokens", "users", ["user_id"], ["id"])
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("token", sa.String, nullable=False, unique=True),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("email_tokens")
    op.drop_table("users")
