
from flask import Blueprint, render_template

from app.extensions import db
from app.database import TransactionDB

transactions_bp = Blueprint(
    "transactions",
    __name__
)


@transactions_bp.route("/")
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
