
import csv
from datetime import date

from sqlalchemy import select

from app.database import SessionLocal, TransactionDB, CategoryDB


def migrate_csv(csv_path):
    imported = 0
    duplicates = 0
    skipped = 0

    with SessionLocal() as session:

        # Load existing categories into a dictionary
        categories = {
            category.name: category
            for category in session.scalars(
                select(CategoryDB)
            ).all()
        }

        # Collect existing transactions to prevent duplicates
        existing_records = {
            (
                item.amount,
                item.category.name,
                item.description,
                item.transaction_date,
                item.type
            )
            for item in session.scalars(
                select(TransactionDB)
            ).all()
        }

        with open(csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    amount = float(row["amount"])
                    category_name = row["category"].strip()
                    description = row["description"].strip()
                    transaction_date = date.fromisoformat(row["date"])
                    transaction_type = row["type"].strip()

                    # Validate transaction
                    if (
                        amount <= 0
                        or not category_name
                        or not description
                        or transaction_type not in ("income", "expense")
                    ):
                        raise ValueError("Invalid transaction")

                    record = (
                        amount,
                        category_name,
                        description,
                        transaction_date,
                        transaction_type
                    )

                    # Skip existing transactions
                    if record in existing_records:
                        duplicates += 1
                        continue

                    # Find or create the category
                    category = categories.get(category_name)

                    if category is None:
                        category = CategoryDB(name=category_name)
                        session.add(category)
                        categories[category_name] = category

                    # Create transaction using CategoryDB relationship
                    transaction = TransactionDB(
                        amount=amount,
                        category=category,
                        description=description,
                        transaction_date=transaction_date,
                        type=transaction_type
                    )

                    session.add(transaction)
                    existing_records.add(record)
                    imported += 1

                except (ValueError, TypeError, KeyError, AttributeError):
                    skipped += 1

        session.commit()

    print("CSV Migration Completed!")
    print("Imported:", imported)
    print("Duplicates:", duplicates)
    print("Skipped:", skipped)


if __name__ == "__main__":
    migrate_csv("transactions_import.csv")
