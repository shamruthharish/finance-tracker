from flask import Blueprint

budget_bp = Blueprint(
    "budget",
    __name__
)


@budget_bp.route("/")
def list_budgets():
    return "Budget Page"