
from datetime import date
import math

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
)

from flask_login import login_required, current_user
from flask import render_template, request
from app.extensions import db
from sqlalchemy import or_

from app import db
from app.database import TransactionDB, CategoryDB


transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/")
@login_required
def list_transactions():

    # 1. Get filter values from URL
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    # 2. Start with the current user's transactions
    query = db.select(TransactionDB).where(
        TransactionDB.user_id == current_user.id
    )

    # 3. Search by description
    if search:
        query = query.where(
            TransactionDB.description.ilike(f"%{search}%")
        )

    # 4. Filter by category
    if category_id:
        try:
            category_id = int(category_id)

            query = query.where(
                TransactionDB.category_id == category_id
            )
        except ValueError:
            category_id = ""

    # 5. Filter by starting date
    if start_date:
        try:
            start_date = date.fromisoformat(start_date)

            query = query.where(
                TransactionDB.transaction_date >= start_date
            )
        except ValueError:
            start_date = ""

    # 6. Filter by ending date
    if end_date:
        try:
            end_date = date.fromisoformat(end_date)

            query = query.where(
                TransactionDB.transaction_date <= end_date
            )
        except ValueError:
            end_date = ""

    # 7. Sort newest transactions first
    query = query.order_by(
        TransactionDB.transaction_date.desc()
    )

    # 8. Paginate - 10 transactions per page
    page = request.args.get("page", 1, type=int)

    pagination = db.paginate(
        query,
        page=page,
        per_page=10,
        error_out=False
    )

    # 9. Get categories used by this user's transactions
    categories = db.session.scalars(
        db.select(CategoryDB)
        .join(TransactionDB)
        .where(TransactionDB.user_id == current_user.id)
        .distinct()
        .order_by(CategoryDB.name)
    ).all()

    # 10. Send results to HTML
    return render_template(
        "transactions.html",
        transactions=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category=category_id,
        start_date=start_date.isoformat() if isinstance(start_date, date) else start_date,
        end_date=end_date.isoformat() if isinstance(end_date, date) else end_date
    )


@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    categories = db.session.execute(
        db.select(CategoryDB).order_by(CategoryDB.name)
    ).scalars().all()

    if request.method == "POST":
        amount_text = request.form.get("amount", "").strip()
        category_text = request.form.get("category_id", "").strip()
        description = request.form.get("description", "").strip()
        date_text = request.form.get("transaction_date", "").strip()
        transaction_type = request.form.get("type", "").strip().lower()

        error = None

        # Validate amount
        try:
            amount = float(amount_text)

            if not math.isfinite(amount) or amount <= 0:
                error = "Amount must be a valid number greater than zero."

        except ValueError:
            error = "Please enter a valid amount."

        # Validate category
        category = None

        if not error:
            try:
                category_id = int(category_text)
                category = db.session.get(CategoryDB, category_id)

                if category is None:
                    error = "Please select a valid category."

            except ValueError:
                error = "Please select a valid category."

        # Validate description
        if not error and (
            not description or len(description) > 255
        ):
            error = "Description must contain 1–255 characters."

        # Validate date
        transaction_date = None

        if not error:
            try:
                transaction_date = date.fromisoformat(date_text)
            except ValueError:
                error = "Please enter a valid date."

        # Validate transaction type
        if not error and transaction_type not in ("income", "expense"):
            error = "Please select income or expense."

        if error:
            return render_template(
                "add_transaction.html",
                categories=categories,
                error=error,
                form_data=request.form
            )

        # Save transaction
        transaction = TransactionDB(
            user_id=current_user.id,
            amount=amount,
            category_id=category.id,
            description=description,
            transaction_date=transaction_date,
            type=transaction_type
        )

        try:
            db.session.add(transaction)
            db.session.commit()

        except Exception:
            db.session.rollback()

            return render_template(
                "add_transaction.html",
                categories=categories,
                error="Could not save the transaction. Please try again.",
                form_data=request.form
            )

        return redirect(url_for("transactions.list_transactions"))

    return render_template(
        "add_transaction.html",
        categories=categories,
        error=None,
        form_data={}
    )


@transactions_bp.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    transaction = db.session.execute(
        db.select(TransactionDB).where(
            TransactionDB.id == transaction_id,
            TransactionDB.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if transaction is None:
        abort(404)

    categories = db.session.execute(
        db.select(CategoryDB).order_by(CategoryDB.name)
    ).scalars().all()

    if request.method == "POST":
        amount_text = request.form.get("amount", "").strip()
        category_text = request.form.get("category_id", "").strip()
        description = request.form.get("description", "").strip()
        date_text = request.form.get("transaction_date", "").strip()
        transaction_type = request.form.get("type", "").strip().lower()

        error = None

        try:
            amount = float(amount_text)

            if not math.isfinite(amount) or amount <= 0:
                error = "Enter an amount greater than zero."

        except ValueError:
            error = "Enter a valid amount."

        category = None

        if not error:
            try:
                category = db.session.get(
                    CategoryDB, int(category_text)
                )

                if category is None:
                    error = "Select a valid category."

            except ValueError:
                error = "Select a valid category."

        if not error and (
            not description or len(description) > 255
        ):
            error = "Description must contain 1–255 characters."

        transaction_date = None

        if not error:
            try:
                transaction_date = date.fromisoformat(date_text)
            except ValueError:
                error = "Enter a valid date."

        if not error and transaction_type not in ("income", "expense"):
            error = "Select income or expense."

        if error:
            return render_template(
                "edit_transaction.html",
                transaction=transaction,
                categories=categories,
                error=error,
                form_data=request.form
            )

        transaction.amount = amount
        transaction.category_id = category.id
        transaction.description = description
        transaction.transaction_date = transaction_date
        transaction.type = transaction_type

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            return render_template(
                "edit_transaction.html",
                transaction=transaction,
                categories=categories,
                error="Could not update transaction.",
                form_data=request.form
            )

        return redirect(url_for("transactions.list_transactions"))

    return render_template(
        "edit_transaction.html",
        transaction=transaction,
        categories=categories,
        error=None,
        form_data={
            "amount": str(transaction.amount),
            "category_id": str(transaction.category_id),
            "description": transaction.description,
            "transaction_date": transaction.transaction_date.isoformat(),
            "type": transaction.type
        }
    )


@transactions_bp.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    transaction = db.session.execute(
        db.select(TransactionDB).where(
            TransactionDB.id == transaction_id,
            TransactionDB.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if transaction is None:
        abort(404)

    try:
        db.session.delete(transaction)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500)

    return redirect(url_for("transactions.list_transactions"))
