
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

from flask_login import login_required

from app.extensions import db
from app.database import TransactionDB, CategoryDB


transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/")
@login_required
def list_transactions():
    transactions = db.session.execute(
        db.select(TransactionDB).order_by(
            TransactionDB.transaction_date.desc()
        )
    ).scalars().all()

    return render_template(
        "transactions.html",
        transactions=transactions
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
    transaction = db.session.get(TransactionDB, transaction_id)

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
    transaction = db.session.get(TransactionDB, transaction_id)

    if transaction is None:
        abort(404)

    try:
        db.session.delete(transaction)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500)

    return redirect(url_for("transactions.list_transactions"))
