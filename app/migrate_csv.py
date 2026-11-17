
import csv
from datetime import date

from app.database import SessionLocal, TransactionDB


def migrate_csv(csv_path):
    imported = 0
    duplicates = 0
    skipped = 0

    with SessionLocal() as session:

        # Collect existing transactions to prevent duplicates
        existing_records = {
            (
                item.amount,
                item.category,
                item.description,
                item.transaction_date,
                item.type
            )
            for item in session.query(TransactionDB).all()
        }

        with open(csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    amount = float(row["amount"])
                    category = row["category"].strip()
                    description = row["description"].strip()
                    transaction_date = date.fromisoformat(row["date"])
                    transaction_type = row["type"].strip()

                    # Validate transaction
                    if (
                        amount <= 0
                        or not category
                        or not description
                        or transaction_type not in ("income", "expense")
                    ):
                        raise ValueError("Invalid transaction")

                    record = (
                        amount,
                        category,
                        description,
                        transaction_date,
                        transaction_type
                    )

                    # Skip existing transactions
                    if record in existing_records:
                        duplicates += 1
                        continue

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
