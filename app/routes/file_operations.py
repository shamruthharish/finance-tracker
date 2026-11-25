
import csv
import io
import json
import math
import uuid

from datetime import date
from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_file,
    session,
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.database import TransactionDB, CategoryDB


file_bp = Blueprint("file_operations", __name__)


REQUIRED_COLUMNS = {
    "transaction_date",
    "amount",
    "category",
    "description",
    "type",
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def validate_csv_rows(rows):
    valid_rows = []
    errors = []

    categories = db.session.execute(
        db.select(CategoryDB)
    ).scalars().all()

    category_lookup = {
        category.name.strip().lower(): category.id
        for category in categories
    }

    if len(rows) > 5000:
        return [], ["CSV cannot contain more than 5000 transactions."]

    for row_number, row in enumerate(rows, start=2):

        try:
            amount = float(row["amount"])

            if not math.isfinite(amount) or amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            transaction_date = date.fromisoformat(
                row["transaction_date"].strip()
            )

            category_name = row["category"].strip().lower()

            if category_name not in category_lookup:
                raise ValueError(
                    f"Unknown category: {row['category']}"
                )

            description = row["description"].strip()

            if not description or len(description) > 255:
                raise ValueError(
                    "Description must contain 1-255 characters."
                )

            transaction_type = row["type"].strip().lower()

            if transaction_type not in ("income", "expense"):
                raise ValueError(
                    "Type must be income or expense."
                )

            valid_rows.append({
                "amount": amount,
                "transaction_date": transaction_date.isoformat(),
                "category_id": category_lookup[category_name],
                "description": description,
                "type": transaction_type,
            })

        except (ValueError, KeyError, AttributeError, TypeError) as error:
            errors.append(
                f"Row {row_number}: {error}"
            )

    return valid_rows, errors


@file_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_transactions():

    if request.method == "POST":

        uploaded_file = request.files.get("file")

        if not uploaded_file or not uploaded_file.filename:
            flash("Please select a CSV file.", "warning")
            return redirect(url_for("file_operations.import_transactions"))

        filename = secure_filename(uploaded_file.filename)

        if not filename or not allowed_file(filename):
            flash("Only CSV files are allowed.", "danger")
            return redirect(url_for("file_operations.import_transactions"))

        try:
            content = uploaded_file.read().decode("utf-8-sig")

            reader = csv.DictReader(io.StringIO(content))

            if not reader.fieldnames:
                raise ValueError("CSV file is empty.")

            reader.fieldnames = [
                name.strip() if name else ""
                for name in reader.fieldnames
            ]

            if (
                len(reader.fieldnames) != len(set(reader.fieldnames))
                or set(reader.fieldnames) != REQUIRED_COLUMNS
            ):
                raise ValueError(
                    "CSV must contain exactly these columns: "
                    "transaction_date, amount, category, "
                    "description, type."
                )

            rows = list(reader)

            if not rows:
                raise ValueError("CSV contains no transactions.")

            valid_rows, errors = validate_csv_rows(rows)

            if errors:
                return render_template(
                    "import.html",
                    errors=errors,
                    preview=[],
                )

            token = uuid.uuid4().hex

            upload_folder = Path(
                current_app.config["UPLOAD_FOLDER"]
            )

            upload_folder.mkdir(parents=True, exist_ok=True)

            pending_file = upload_folder / f"{token}.json"

            pending_file.write_text(
                json.dumps({
                    "user_id": current_user.id,
                    "rows": valid_rows,
                }),
                encoding="utf-8",
            )

            old_token = session.get("pending_import")

            if old_token:
                old_file = upload_folder / f"{old_token}.json"
                old_file.unlink(missing_ok=True)

            session["pending_import"] = token

            return render_template(
                "preview_import.html",
                preview=valid_rows[:5],
                total=len(valid_rows),
            )

        except (UnicodeDecodeError, csv.Error, ValueError):
            flash(
                "Invalid CSV file. Check its encoding and contents.",
                "danger",
            )

        except OSError:
            flash("Could not process the uploaded file.", "danger")

        return redirect(
            url_for("file_operations.import_transactions")
        )

    return render_template(
        "import.html",
        errors=[],
        preview=[],
    )


@file_bp.route("/import/confirm", methods=["POST"])
@login_required
def confirm_import():

    token = session.get("pending_import")

    if not token or not token.isalnum() or len(token) != 32:
        flash("No pending import found.", "warning")
        return redirect(url_for("file_operations.import_transactions"))

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    pending_file = upload_folder / f"{token}.json"

    try:
        data = json.loads(pending_file.read_text(encoding="utf-8"))

        if data.get("user_id") != current_user.id:
            flash("Invalid import session.", "danger")
            return redirect(
                url_for("file_operations.import_transactions")
            )

        transactions = []

        for row in data["rows"]:
            category = db.session.get(
                CategoryDB, row["category_id"]
            )

            if category is None:
                raise ValueError("A category no longer exists.")

            transactions.append(
                TransactionDB(
                    user_id=current_user.id,
                    amount=row["amount"],
                    category_id=row["category_id"],
                    description=row["description"],
                    transaction_date=date.fromisoformat(
                        row["transaction_date"]
                    ),
                    type=row["type"],
                )
            )

        if not transactions:
            raise ValueError("No transactions to import.")

        db.session.add_all(transactions)
        db.session.commit()

        flash(
            f"Successfully imported {len(transactions)} transactions.",
            "success",
        )

    except (OSError, ValueError, KeyError, TypeError):
        db.session.rollback()
        flash("Import failed. Please upload the CSV again.", "danger")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("CSV import failed")
        flash("Database error while importing transactions.", "danger")

    finally:
        pending_file.unlink(missing_ok=True)
        session.pop("pending_import", None)

    return redirect(url_for("transactions.list_transactions"))


def get_filtered_transactions():

    query = (
        db.select(TransactionDB, CategoryDB.name)
        .join(
            CategoryDB,
            TransactionDB.category_id == CategoryDB.id,
        )
        .where(TransactionDB.user_id == current_user.id)
    )

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    category_id = request.args.get("category_id", "").strip()

    if start_date:
        query = query.where(
            TransactionDB.transaction_date >= date.fromisoformat(
                start_date
            )
        )

    if end_date:
        query = query.where(
            TransactionDB.transaction_date <= date.fromisoformat(
                end_date
            )
        )

    if category_id:
        query = query.where(
            TransactionDB.category_id == int(category_id)
        )

    query = query.order_by(
        TransactionDB.transaction_date.desc()
    )

    return db.session.execute(query).all()




@file_bp.route("/export/options")
@login_required
def export_options():

    categories = db.session.execute(
        db.select(CategoryDB).order_by(CategoryDB.name)
    ).scalars().all()

    return render_template(
        "export_options.html",
        categories=categories,
    )

@file_bp.route("/export")
@login_required
def export_transactions():

    try:
        transactions = get_filtered_transactions()

    except ValueError:
        flash("Invalid date or category filter.", "danger")
        return redirect(url_for("transactions.list_transactions"))

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "transaction_date",
        "amount",
        "category",
        "description",
        "type",
    ])

    for transaction, category_name in transactions:
        writer.writerow([
            transaction.transaction_date.isoformat(),
            transaction.amount,
            category_name,
            transaction.description,
            transaction.type,
        ])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="finance_transactions.csv",
    )


@file_bp.route("/export/pdf")
@login_required
def export_pdf():

    try:
        transactions = get_filtered_transactions()

    except ValueError:
        flash("Invalid date or category filter.", "danger")
        return redirect(url_for("transactions.list_transactions"))

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm

    output = io.BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Finance Tracker Report", styles["Title"]),
        Spacer(1, 10),
        Paragraph(
            f"User: {current_user.username}",
            styles["Normal"],
        ),
        Spacer(1, 15),
    ]

    total_income = sum(
        row.amount
        for row, _ in transactions
        if row.type == "income"
    )

    total_expense = sum(
        row.amount
        for row, _ in transactions
        if row.type == "expense"
    )

    elements.append(
        Paragraph(
            f"Total Income: {total_income:.2f} | "
            f"Total Expenses: {total_expense:.2f}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 15))

    table_data = [[
        "Date",
        "Amount",
        "Category",
        "Description",
        "Type",
    ]]

    for transaction, category_name in transactions:
        table_data.append([
            transaction.transaction_date.isoformat(),
            f"{transaction.amount:.2f}",
            category_name,
            transaction.description[:40],
            transaction.type,
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[25 * mm, 22 * mm, 30 * mm, 75 * mm, 20 * mm],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)

    document.build(elements)

    output.seek(0)

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="finance_report.pdf",
    )
