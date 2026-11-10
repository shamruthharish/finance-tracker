
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Finance Tracker - Manage your expenses"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # Add expense command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new expense"
    )

    add_parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Expense amount"
    )

    add_parser.add_argument(
        "--category",
        type=str,
        required=True,
        help="Expense category"
    )

    # List expenses command
    subparsers.add_parser(
        "list",
        help="Display all expenses"
    )

    args = parser.parse_args()

    if args.command == "add":
        print(f"Expense amount: ₹{args.amount}")
        print(f"Category: {args.category}")

    elif args.command == "list":
        print("Displaying expenses...")


if __name__ == "__main__":
    main()
