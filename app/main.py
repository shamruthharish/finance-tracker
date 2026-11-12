
import argparse
import json
from pathlib import Path

from colorama import Fore, Style, init
from tabulate import tabulate

from app.models import Category, Transaction

init(autoreset=True)

DATA_FILE = Path(__file__).resolve().parent / "transactions.json"


def load_transactions() -> list[dict]:
    """Load saved transactions from JSON."""
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_transactions(transactions: list[dict]) -> None:
    """Save transactions to JSON storage."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(transactions, file, indent=4)


def add_transaction(args: argparse.Namespace) -> None:
    """Validate and save a new transaction."""

    transaction = Transaction(
        args.amount,
        Category(args.category),
        args.description or args.category
    )

    records = load_transactions()

    records.append({
        "amount": transaction.amount,
        "category": transaction.category.name,
        "description": transaction.description,
        "date": transaction.transaction_date.isoformat(),
        "type": args.type
    })

    save_transactions(records)

    print(Fore.GREEN + "\n✓ Transaction saved successfully!")
    print(f"  Description : {transaction.description}")
    print(f"  Category    : {transaction.category}")
    print(f"  Amount      : ₹{transaction.amount:,.2f}")
    print(f"  Type        : {args.type.title()}")


def list_transactions() -> None:
    """Display all saved transactions."""

    records = load_transactions()

    if not records:
        print(Fore.YELLOW + "\nNo transactions found.")
        return

    table = [
        [
            record["description"],
            record["category"],
            record["type"].title(),
            f"₹{record['amount']:,.2f}",
            record["date"]
        ]
        for record in records
    ]

    print("\n" + Fore.CYAN + Style.BRIGHT + "TRANSACTION HISTORY")
    print(tabulate(
        table,
        headers=["Description", "Category", "Type", "Amount", "Date"],
        tablefmt="rounded_grid"
    ))


def show_dashboard() -> None:
    """Display the overall financial summary."""

    records = load_transactions()

    income = sum(
        record["amount"]
        for record in records
        if record["type"] == "income"
    )

    expenses = sum(
        record["amount"]
        for record in records
        if record["type"] == "expense"
    )

    balance = income - expenses

    print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 55)
    print("               FINANCE TRACKER PRO")
    print("=" * 55)

    print(Fore.GREEN + f"\n  TOTAL INCOME   : ₹{income:,.2f}")
    print(Fore.RED + f"  TOTAL EXPENSES : ₹{expenses:,.2f}")
    print(Fore.YELLOW + f"  NET BALANCE    : ₹{balance:,.2f}")

    print(Fore.CYAN + "\n" + "-" * 55)
    print(f"  TOTAL TRANSACTIONS: {len(records)}")
    print("-" * 55)

    if records:
        list_transactions()

    print(Fore.CYAN + "\n" + "=" * 55)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Finance Tracker Pro - Manage your finances"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands"
    )

    add_parser = subparsers.add_parser(
        "add",
        help="Add a new transaction"
    )

    add_parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Transaction amount"
    )

    add_parser.add_argument(
        "--category",
        type=str,
        required=True,
        help="Transaction category"
    )

    add_parser.add_argument(
        "--description",
        type=str,
        help="Transaction description"
    )

    add_parser.add_argument(
        "--type",
        choices=["income", "expense"],
        default="expense",
        help="Transaction type"
    )

    subparsers.add_parser(
        "list",
        help="Display all transactions"
    )

    subparsers.add_parser(
        "dashboard",
        help="Display financial dashboard"
    )

    args = parser.parse_args()

    try:
        if args.command == "add":
            add_transaction(args)

        elif args.command == "list":
            list_transactions()

        elif args.command == "dashboard":
            show_dashboard()

    except (ValueError, TypeError) as error:
        print(Fore.RED + f"\nError: {error}")


if __name__ == "__main__":
    main()
