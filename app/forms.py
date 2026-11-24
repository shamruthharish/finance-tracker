
from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    SelectField,
    DateField,
    StringField
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Length
)


class TransactionForm(FlaskForm):

    amount = DecimalField(
        "Amount",
        validators=[
            DataRequired(message="Amount is required."),
            NumberRange(
                min=0.01,
                message="Amount must be greater than zero."
            )
        ]
    )

    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[
            DataRequired(message="Please select a category.")
        ]
    )

    description = StringField(
        "Description",
        validators=[
            DataRequired(message="Description is required."),
            Length(
                max=255,
                message="Description cannot exceed 255 characters."
            )
        ]
    )

    transaction_date = DateField(
        "Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(message="Please enter a valid date.")
        ]
    )

    type = SelectField(
        "Transaction Type",
        choices=[
            ("income", "Income"),
            ("expense", "Expense")
        ],
        validators=[
            DataRequired(message="Please select a transaction type.")
        ]
    )
