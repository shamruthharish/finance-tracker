
"""add transaction cascade delete

Revision ID: 61ab613a5a73
Revises: 6f31d1f2cf6d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '61ab613a5a73'
down_revision: Union[str, Sequence[str], None] = '6f31d1f2cf6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Give the existing unnamed foreign key a recognizable name
NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
}


def upgrade() -> None:
    """Add ON DELETE CASCADE to transaction category foreign key."""

    with op.batch_alter_table(
        "transactions",
        naming_convention=NAMING_CONVENTION,
        recreate="always"
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_transactions_category_id_categories",
            type_="foreignkey"
        )

        batch_op.create_foreign_key(
            "fk_transactions_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="CASCADE"
        )


def downgrade() -> None:
    """Remove ON DELETE CASCADE from transaction category foreign key."""

    with op.batch_alter_table(
        "transactions",
        naming_convention=NAMING_CONVENTION,
        recreate="always"
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_transactions_category_id_categories",
            type_="foreignkey"
        )

        batch_op.create_foreign_key(
            "fk_transactions_category_id_categories",
            "categories",
            ["category_id"],
            ["id"]
        )
