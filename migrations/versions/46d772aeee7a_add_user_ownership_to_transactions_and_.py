"""add user ownership to transactions and budgets

Revision ID: 46d772aeee7a
Revises: 5cc699efa53a
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '46d772aeee7a'
down_revision: Union[str, Sequence[str], None] = '5cc699efa53a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable ownership columns first so existing records can be preserved.
    with op.batch_alter_table("transactions", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column("user_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_transactions_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE"
        )
        batch_op.create_index(
            "ix_transactions_user_id",
            ["user_id"]
        )

    with op.batch_alter_table("budgets", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column("user_id", sa.Integer(), nullable=True)
        )
        batch_op.drop_constraint(
            "unique_category_month_budget",
            type_="unique"
        )
        batch_op.create_foreign_key(
            "fk_budgets_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE"
        )
        batch_op.create_unique_constraint(
            "unique_user_category_month_budget",
            ["user_id", "category_id", "month", "year"]
        )
        batch_op.create_index(
            "ix_budgets_user_id",
            ["user_id"]
        )

    # Assign all existing records to the original account.
    op.execute(
        sa.text("UPDATE transactions SET user_id = 1")
    )
    op.execute(
        sa.text("UPDATE budgets SET user_id = 1")
    )

    # Ownership is now mandatory.
    with op.batch_alter_table("transactions", recreate="always") as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False
        )

    with op.batch_alter_table("budgets", recreate="always") as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False
        )


def downgrade() -> None:
    with op.batch_alter_table("transactions", recreate="always") as batch_op:
        batch_op.drop_index("ix_transactions_user_id")
        batch_op.drop_constraint(
            "fk_transactions_user_id_users",
            type_="foreignkey"
        )
        batch_op.drop_column("user_id")

    with op.batch_alter_table("budgets", recreate="always") as batch_op:
        batch_op.drop_index("ix_budgets_user_id")
        batch_op.drop_constraint(
            "unique_user_category_month_budget",
            type_="unique"
        )
        batch_op.drop_constraint(
            "fk_budgets_user_id_users",
            type_="foreignkey"
        )
        batch_op.drop_column("user_id")
        batch_op.create_unique_constraint(
            "unique_category_month_budget",
            ["category_id", "month", "year"]
        )
