
from datetime import date
import math

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from app.extensions import db
from app.database import BudgetDB, CategoryDB
from flask_login import login_required, current_user

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/")
@login_required
def list_budgets():

    budgets = db.session.execute(
        db.select(BudgetDB)
        .where(BudgetDB.user_id == current_user.id)
        .order_by(
            BudgetDB.year.desc(),
            BudgetDB.month.desc()
        )
    ).scalars().all()

    return render_template(
        "budgets.html",
        budgets=budgets
    )


@budget_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_budget():
    today_year=date.today().year
    categories = db.session.execute(
        db.select(CategoryDB).order_by(CategoryDB.name)
    ).scalars().all()

    if request.method == "POST":

        category_id = request.form.get("category_id", type=int)
        month = request.form.get("month", type=int)
        year = request.form.get("year", type=int)
        amount_text = request.form.get("limit_amount", "").strip()

        if category_id is None or month is None or year is None:
            flash("Please complete all fields.", "error")
            return render_template(
                "add_budget.html",
                categories=categories
            )

        if not 1 <= month <= 12:
            flash("Please select a valid month.", "error")
            return render_template(
                "add_budget.html",
                categories=categories
            )

        if not 2000 <= year <= 2100:
            flash("Please enter a valid year.", "error")
            return render_template(
                "add_budget.html",
                categories=categories
            )

        try:
            amount = float(amount_text)
        except ValueError:
            amount = 0

        if not math.isfinite(amount) or amount <= 0:
            flash("Budget amount must be greater than zero.", "error")
            return render_template(
                "add_budget.html",
                categories=categories
            )

        category = db.session.get(CategoryDB, category_id)

        if category is None:
            flash("Selected category does not exist.", "error")
            return render_template(
                "add_budget.html",
                categories=categories
            )

        existing_budget = db.session.execute(
            db.select(BudgetDB).where(
                BudgetDB.user_id == current_user.id,
                BudgetDB.category_id == category_id,
                BudgetDB.month == month,
                BudgetDB.year == year
            )
        ).scalar_one_or_none()

        if existing_budget:
            flash(
                "A budget already exists for this category and month.",
                "error"
            )
            return render_template(
                "add_budget.html",
                categories=categories
            )

        budget = BudgetDB(
            user_id=current_user.id,
            category_id=category_id,
            month=month,
            year=year,
            limit_amount=amount
        )

        db.session.add(budget)
        db.session.commit()

        flash("Budget added successfully!", "success")

        return redirect(url_for("budget.list_budgets"))

    return render_template(
        "add_budget.html",
        categories=categories
    )
