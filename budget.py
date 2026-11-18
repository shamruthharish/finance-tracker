
from datetime import date
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import BudgetDB, TransactionDB
from app.exceptions import BudgetExceededError


def check_budget(
    session: Session,
    category_id: int,
    month: int,
    year: int
) -> Decimal:

    # Validate month
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")

    # Find the monthly budget
    budget = session.scalar(
        select(BudgetDB).where(
            BudgetDB.category_id == category_id,
            BudgetDB.month == month,
            BudgetDB.year == year
        )
    )

    if budget is None:
        raise ValueError("No budget found for this category.")

    # Calculate monthly date range
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    # Calculate total expenses
    total_spent = session.scalar(
        select(
            func.coalesce(func.sum(TransactionDB.amount), 0.0)
        ).where(
            TransactionDB.category_id == category_id,
            TransactionDB.type == "expense",
            TransactionDB.transaction_date >= start_date,
            TransactionDB.transaction_date < end_date
        )
    )

    # Convert to Decimal for comparison
    spent = Decimal(str(total_spent))
    limit = Decimal(str(budget.limit_amount))

    # Check whether budget is exceeded
    if spent > limit:
        exceeded = spent - limit
        raise BudgetExceededError(
            f"Budget exceeded! "
            f"Spent: Rs.{spent}, "
            f"Limit: Rs.{limit}, "
            f"Exceeded: Rs.{exceeded}"
        )

    # Return remaining budget
    return limit - spent

def check_all_budgets(
    session: Session,
    month: int,
    year: int
) -> None:
    """Display the budget status of every category for a month."""

    budgets = session.scalars(
        select(BudgetDB).where(
            BudgetDB.month == month,
            BudgetDB.year == year
        )
    ).all()

    if not budgets:
        print("No budgets found for this month.")
        return

    for budget in budgets:
        category_name = budget.category.name

        try:
            remaining = check_budget(
                session,
                budget.category_id,
                month,
                year
            )

            print(
                f"\033[92m{category_name}: "
                f"Within budget. Remaining: Rs.{remaining}\033[0m"
            )

        except BudgetExceededError as error:
            print(
                f"\033[91m{category_name}: "
                f"{error}\033[0m"
            )
