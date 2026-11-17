
import csv
import json
import pytest
from jsonschema import ValidationError
from unittest.mock import patch

from app import io_manager


@pytest.fixture
def valid_record():
    return {
        "amount": 500,
        "category": "Food",
        "description": "Lunch",
        "date": "2026-11-17",
        "type": "expense"
    }


def test_validate_transaction(valid_record):
    transaction = io_manager.validate_transaction(valid_record)
    assert transaction.amount == 500
    assert transaction.category.name == "Food"


def test_invalid_amount_schema(valid_record):
    valid_record["amount"] = -100
    with pytest.raises(ValidationError):
        io_manager.validate_transaction(valid_record)


def test_invalid_date_schema(valid_record):
    valid_record["date"] = "wrong-date"
    with pytest.raises(ValidationError):
        io_manager.validate_transaction(valid_record)


def test_load_transactions_empty(tmp_path, monkeypatch):
    data_file = tmp_path / "transactions.json"
    monkeypatch.setattr(io_manager, "DATA_FILE", data_file)

    assert io_manager.load_transactions() == []


def test_save_and_load_transactions(tmp_path, monkeypatch, valid_record):
    data_file = tmp_path / "transactions.json"
    monkeypatch.setattr(io_manager, "DATA_FILE", data_file)

    io_manager.save_transactions([valid_record])
    result = io_manager.load_transactions()

    assert result == [valid_record]


def test_import_csv(tmp_path, monkeypatch):
    data_file = tmp_path / "transactions.json"
    csv_file = tmp_path / "sample.csv"

    monkeypatch.setattr(io_manager, "DATA_FILE", data_file)

    with csv_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["amount", "category", "description", "date", "type"])
        writer.writerow(["500", "Food", "Lunch", "2026-11-17", "expense"])
        writer.writerow(["-100", "Food", "Invalid", "2026-11-17", "expense"])

    imported, skipped = io_manager.import_csv(csv_file)

    assert imported == 1
    assert skipped == 1
    assert len(io_manager.load_transactions()) == 1


def test_import_csv_invalid_headers(tmp_path, monkeypatch):
    csv_file = tmp_path / "wrong.csv"

    monkeypatch.setattr(
        io_manager, "DATA_FILE", tmp_path / "transactions.json"
    )

    csv_file.write_text("name,price\nLunch,500\n")

    with pytest.raises(ValueError):
        io_manager.import_csv(csv_file)


def test_export_json(tmp_path, monkeypatch, valid_record):
    data_file = tmp_path / "transactions.json"
    output_file = tmp_path / "export.json"

    monkeypatch.setattr(io_manager, "DATA_FILE", data_file)
    io_manager.save_transactions([valid_record])

    count = io_manager.export_json(output_file)

    assert count == 1

    with output_file.open("r", encoding="utf-8") as file:
        exported = json.load(file)

    assert exported[0]["description"] == "Lunch"


def test_export_skips_invalid_records(tmp_path, monkeypatch, valid_record):
    data_file = tmp_path / "transactions.json"
    output_file = tmp_path / "export.json"

    invalid_record = valid_record.copy()
    invalid_record["amount"] = -500

    monkeypatch.setattr(io_manager, "DATA_FILE", data_file)
    io_manager.save_transactions([valid_record, invalid_record])

    with patch.object(io_manager.logger, "warning") as warning_mock:
        count = io_manager.export_json(output_file)

    assert count == 1
    warning_mock.assert_called_once()
