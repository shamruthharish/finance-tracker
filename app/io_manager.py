
import csv
import json
import logging

from datetime import date
from pathlib import Path

from jsonschema import validate, ValidationError, FormatChecker

from app.models import Category, Transaction


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "app" / "transactions.json"

logger = logging.getLogger("finance_tracker")


# Required transaction structure
TRANSACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {
            "type": "number",
            "exclusiveMinimum": 0
        },
        "category": {
            "type": "string",
            "minLength": 1
        },
        "description": {
            "type": "string",
            "minLength": 1
        },
        "date": {
            "type": "string",
            "format": "date"
        },
        "type": {
            "type": "string",
            "enum": ["income", "expense"]
        }
    },
    "required": [
        "amount",
        "category",
        "description",
        "date",
        "type"
    ],
    "additionalProperties": False
}


def load_transactions():
    """Load existing transactions from JSON."""

    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Transaction JSON must contain a list.")

    return records


def save_transactions(records):
    """Save transactions to JSON."""

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    logger.info("Saved %d transactions to JSON.", len(records))


def validate_transaction(record):
    """Validate transaction structure and model values."""

    validate(
        instance=record,
        schema=TRANSACTION_SCHEMA,
        format_checker=FormatChecker()
    )

    transaction_date = date.fromisoformat(record["date"])

    transaction = Transaction(
        amount=record["amount"],
        category=Category(record["category"]),
        description=record["description"],
        transaction_date=transaction_date
    )

    return transaction


def import_csv(csv_path):
    """Import valid transactions from a CSV file."""

    csv_path = Path(csv_path)

    required_columns = {
        "amount",
        "category",
        "description",
        "date",
        "type"
    }

    records = load_transactions()

    imported = 0
    skipped = 0

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames or set(reader.fieldnames) != required_columns:
            raise ValueError("CSV headers do not match the required columns.")

        for row_number, row in enumerate(reader, start=2):

            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("Missing or extra CSV values.")

                record = {
                    "amount": float(row["amount"]),
                    "category": row["category"].strip(),
                    "description": row["description"].strip(),
                    "date": row["date"].strip(),
                    "type": row["type"].strip().lower()
                }

                validate_transaction(record)

                records.append(record)
                imported += 1

                logger.info(
                    "Imported CSV row %d: %s",
                    row_number,
                    record["description"]
                )

            except (ValueError, TypeError, ValidationError) as error:

                skipped += 1

                logger.warning(
                    "Skipped CSV row %d: %s",
                    row_number,
                    error
                )

    save_transactions(records)

    print("\nCSV Import Completed!")
    print(f"Successfully imported: {imported}")
    print(f"Skipped invalid rows: {skipped}")

    return imported, skipped


def export_json(output_path):
    """Export valid transactions into a JSON file."""

    output_path = Path(output_path)

    records = load_transactions()

    valid_records = []

    for record in records:
        try:
            validate_transaction(record)
            valid_records.append(record)

        except (ValueError, TypeError, ValidationError) as error:
            logger.warning("Skipped invalid stored record: %s", error)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(valid_records, file, indent=4)

    print(f"\nExported {len(valid_records)} valid transactions.")
    print(f"Output file: {output_path}")

    return len(valid_records)
