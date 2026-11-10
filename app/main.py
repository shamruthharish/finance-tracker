import argparse


def main():

    # Create the main argument parser
    parser = argparse.ArgumentParser(
        description="Finance Tracker - Manage your expenses"
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # ADD COMMAND
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

    # LIST COMMAND
    subparsers.add_parser(
        "list",
        help="Display all expenses"
    )

    # Read user input
    args = parser.parse_args()

    # Perform the selected command
    if args.command == "add":

        print(f"Expense amount: ₹{args.amount}")
        print(f"Category: {args.category}")

    elif args.command == "list":

        print("Displaying expenses...")


if __name__ == "__main__":
    main()
    .venv/
__pycache__/
*.pyc
.env
.DS_Store
