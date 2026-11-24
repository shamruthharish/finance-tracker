
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date

from app.extensions import db
from app.database import TransactionDB, CategoryDB


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


@dashboard_bp.route("/")
@login_required
def dashboard():

    # 1. Spending by category
    category_data = (
        db.session.query(
            CategoryDB.name,
            func.sum(TransactionDB.amount)
        )
        .join(
            TransactionDB,
            CategoryDB.id == TransactionDB.category_id
        )
        .filter(
            TransactionDB.user_id == current_user.id,
            TransactionDB.type == "expense"
        )
        .group_by(CategoryDB.name)
        .all()
    )

    category_labels = [
        item[0] for item in category_data
    ]

    category_amounts = [
        float(item[1]) for item in category_data
    ]

    # 2. Generate the last six months
    today = date.today()

    months = []

    for i in range(5, -1, -1):
        month_index = today.month - i
        year = today.year

        while month_index <= 0:
            month_index += 12
            year -= 1

        months.append(date(year, month_index, 1))

    # 3. Retrieve monthly expenses
    start_month = months[0]

    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    monthly_data = (
        db.session.query(
            func.strftime(
                "%Y-%m",
                TransactionDB.transaction_date
            ),
            func.sum(TransactionDB.amount)
        )
        .filter(
            TransactionDB.user_id == current_user.id,
            TransactionDB.type == "expense",
            TransactionDB.transaction_date >= start_month,
            TransactionDB.transaction_date < next_month
        )
        .group_by(
            func.strftime(
                "%Y-%m",
                TransactionDB.transaction_date
            )
        )
        .all()
    )

    monthly_totals = {
        month: float(total)
        for month, total in monthly_data
        if month is not None
    }

    monthly_labels = [
        month.strftime("%b %Y")
        for month in months
    ]

    monthly_amounts = [
        monthly_totals.get(
            month.strftime("%Y-%m"), 0
        )
        for month in months
    ]

    return render_template(
        "dashboard.html",
        category_labels=category_labels,
        category_amounts=category_amounts,
        monthly_labels=monthly_labels,
        monthly_amounts=monthly_amounts
    )
