
from datetime import date

from sqlalchemy import select, func

from app.database import (
    SessionLocal,
    CategoryDB,
    TransactionDB,
)


def category_summary(year=None, month=None, limit=3, session=None):
    """
    Return the highest-spending categories for a given month.

    Result format:
    [
        {"category": "Shopping", "total": 750.0},
        {"category": "Food", "total": 650.0}
    ]
    """

    today = date.today()

    if year is None:
        year = today.year

    if month is None:
        month = today.month

    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    statement = (
        select(
            CategoryDB.name,
            func.sum(TransactionDB.amount).label("total_spent")
        )
        .join(TransactionDB)
        .where(TransactionDB.type == "expense")
        .where(TransactionDB.transaction_date >= start_date)
        .where(TransactionDB.transaction_date < end_date)
        .group_by(CategoryDB.id, CategoryDB.name)
        .order_by(func.sum(TransactionDB.amount).desc())
        .limit(limit)
    )

    # Use an existing session if supplied, otherwise create one.
    owns_session = session is None

    if owns_session:
        session = SessionLocal()

    try:
        rows = session.execute(statement).all()

        return [
            {
                "category": name,
                "total": float(total)
            }
            for name, total in rows
        ]

    finally:
        if owns_session:
            session.close()

import matplotlib.pyplot as plt
from pathlib import Path


def plot_category_summary(results):
    """Create and save a bar chart of category spending."""

    if not results:
        print("No data available to create a chart.")
        return

    categories = [item["category"] for item in results]
    amounts = [item["total"] for item in results]

    plt.figure(figsize=(9, 5))

    plt.bar(categories, amounts)

    plt.title("Monthly Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (Rs.)")

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    for index, amount in enumerate(amounts):
        plt.text(
            index,
            amount,
            f"Rs. {amount:.2f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    output_path = Path(__file__).resolve().parent.parent
    output_path = output_path / "category_spending.png"

    plt.savefig(output_path, dpi=150)

    print(f"\nChart saved successfully: {output_path}")

    plt.show()
    plt.close()


if __name__ == "__main__":

    results = category_summary()

    print("\nMONTHLY SPENDING SUMMARY")
    print("-" * 35)

    if not results:
        print("No expenses found for this month.")

    for item in results:
        print(
            f"{item['category']:<15} "
            f"Rs. {item['total']:.2f}"
        )

    plot_category_summary(results)