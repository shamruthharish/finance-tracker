
"""add category relationship

Revision ID: 85ef71de5c0b
Revises: fe56ecd726af
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '85ef71de5c0b'
down_revision: Union[str, Sequence[str], None] = 'fe56ecd726af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 2. Add category_id temporarily as nullable
    op.add_column(
        'transactions',
        sa.Column('category_id', sa.Integer(), nullable=True)
    )

    # 3. Transfer existing category names
    connection = op.get_bind()

    categories = connection.execute(
        sa.text("SELECT DISTINCT category FROM transactions")
    ).scalars().all()

    for category_name in categories:

        connection.execute(
            sa.text("INSERT INTO categories (name) VALUES (:name)"),
            {"name": category_name}
        )

        category_id = connection.execute(
            sa.text("SELECT id FROM categories WHERE name = :name"),
            {"name": category_name}
        ).scalar_one()

        connection.execute(
            sa.text("""
                UPDATE transactions
                SET category_id = :category_id
                WHERE category = :name
            """),
            {
                "category_id": category_id,
                "name": category_name
            }
        )

    # 4. Make category_id mandatory,
    # add ForeignKey and remove old category column
    with op.batch_alter_table(
        'transactions',
        recreate='always'
    ) as batch_op:

        batch_op.alter_column(
            'category_id',
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.drop_column('category')

        batch_op.create_foreign_key(
            'fk_transactions_category_id_categories',
            'categories',
            ['category_id'],
            ['id']
        )


def downgrade() -> None:

    # 1. Restore the old category column temporarily
    op.add_column(
        'transactions',
        sa.Column('category', sa.String(length=100), nullable=True)
    )

    # 2. Restore category names using the relationship
    connection = op.get_bind()

    connection.execute(
        sa.text("""
            UPDATE transactions
            SET category = (
                SELECT categories.name
                FROM categories
                WHERE categories.id = transactions.category_id
            )
        """)
    )

    # 3. Remove ForeignKey and category_id
    with op.batch_alter_table(
        'transactions',
        recreate='always'
    ) as batch_op:

        batch_op.drop_constraint(
            'fk_transactions_category_id_categories',
            type_='foreignkey'
        )

        batch_op.drop_column('category_id')

        batch_op.alter_column(
            'category',
            existing_type=sa.String(length=100),
            nullable=False
        )

    # 4. Remove categories table
    op.drop_table('categories')
