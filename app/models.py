
"""Domain models for the Finance Tracker application."""

from datetime import date, datetime
import math


class Category:
    """Represent an expense category."""

    __slots__ = ("_name", "_description")

    def __init__(self, name, description="General expenses"):
        """Initialize a category after validating its details."""
        self.name = name
        self.description = description

    @property
    def name(self):
        """Return the category name."""
        return self._name

    @name.setter
    def name(self, value):
        """Validate and update the category name."""
        if not isinstance(value, str):
            raise TypeError("Category name must be a string")
        if not value.strip():
            raise ValueError("Category name cannot be empty")
        self._name = value.strip()

    @property
    def description(self):
        """Return the category description."""
        return self._description

    @description.setter
    def description(self, value):
        """Validate and update the category description."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        if not value.strip():
            raise ValueError("Description cannot be empty")
        self._description = value.strip()

    @classmethod
    def from_name(cls, name):
        """Create a category using only its name."""
        return cls(name)

    def __str__(self):
        """Return a readable category representation."""
        return self.name

    def __eq__(self, other):
        """Compare categories by their names."""
        if not isinstance(other, Category):
            return NotImplemented
        return self.name.casefold() == other.name.casefold()


class Transaction:
    """Represent an individual financial transaction."""

    __slots__ = (
        "_amount",
        "_category",
        "_description",
        "_transaction_date",
    )

    def __init__(
        self,
        amount,
        category,
        description,
        transaction_date=None,
    ):
        """Initialize a transaction after validating its details."""
        self.amount = amount
        self.category = category
        self.description = description

        if transaction_date is None:
            transaction_date = date.today()

        self.transaction_date = transaction_date

    @property
    def amount(self):
        """Return the transaction amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        """Validate and update the transaction amount."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Amount must be a number")

        if not math.isfinite(value):
            raise ValueError("Amount must be a finite number")

        if value <= 0:
            raise ValueError("Amount must be greater than zero")

        self._amount = float(value)

    @property
    def category(self):
        """Return the transaction category."""
        return self._category

    @category.setter
    def category(self, value):
        """Validate and update the transaction category."""
        if not isinstance(value, Category):
            raise TypeError("Category must be a Category object")
        self._category = value

    @property
    def description(self):
        """Return the transaction description."""
        return self._description

    @description.setter
    def description(self, value):
        """Validate and update the transaction description."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        if not value.strip():
            raise ValueError("Description cannot be empty")
        self._description = value.strip()

    @property
    def transaction_date(self):
        """Return the transaction date."""
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value):
        """Validate and update the transaction date."""
        if not isinstance(value, date) or isinstance(value, datetime):
            raise TypeError("Transaction date must be a date object")
        self._transaction_date = value

    @classmethod
    def create(cls, amount, category, description):
        """Create a transaction using today's date."""
        return cls(amount, category, description)

    def __str__(self):
        """Return a readable transaction representation."""
        return (
            f"{self.transaction_date} | "
            f"{self.category} | "
            f"{self.description} | "
            f"₹{self.amount:.2f}"
        )

    def __eq__(self, other):
        """Compare transactions by their details."""
        if not isinstance(other, Transaction):
            return NotImplemented

        return (
            self.amount == other.amount
            and self.category == other.category
            and self.description == other.description
            and self.transaction_date == other.transaction_date
        )

    def __lt__(self, other):
        """Compare transactions by their amounts."""
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.amount < other.amount


class Budget:
    """Represent a spending budget for a category."""

    __slots__ = ("_category", "_limit_amount", "_spent_amount")

    def __init__(self, category, limit_amount, spent_amount=0):
        """Initialize a budget with its spending limit."""
        self.category = category
        self.limit_amount = limit_amount
        self.spent_amount = spent_amount

    @property
    def category(self):
        """Return the budget category."""
        return self._category

    @category.setter
    def category(self, value):
        """Validate and update the budget category."""
        if not isinstance(value, Category):
            raise TypeError("Category must be a Category object")
        self._category = value

    @property
    def limit_amount(self):
        """Return the budget limit."""
        return self._limit_amount

    @limit_amount.setter
    def limit_amount(self, value):
        """Validate and update the budget limit."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Budget limit must be a number")
        if not math.isfinite(value):
            raise ValueError("Budget limit must be finite")
        if value <= 0:
            raise ValueError("Budget limit must be positive")
        self._limit_amount = float(value)

    @property
    def spent_amount(self):
        """Return the amount already spent."""
        return self._spent_amount

    @spent_amount.setter
    def spent_amount(self, value):
        """Validate and update the spent amount."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Spent amount must be a number")
        if not math.isfinite(value):
            raise ValueError("Spent amount must be finite")
        if value < 0:
            raise ValueError("Spent amount cannot be negative")
        self._spent_amount = float(value)

    @property
    def remaining_amount(self):
        """Calculate the remaining budget."""
        return self.limit_amount - self.spent_amount

    @classmethod
    def create(cls, category, limit_amount):
        """Create a budget with zero spending."""
        return cls(category, limit_amount)

    def __str__(self):
        """Return a readable budget representation."""
        return (
            f"{self.category}: ₹{self.spent_amount:.2f} "
            f"spent out of ₹{self.limit_amount:.2f}"
        )


def run_basic_assertions():
    """Run basic tests for all domain models."""

    food = Category("Food", "Daily food expenses")
    transport = Category.from_name("Transport")

    transaction1 = Transaction(
        500, food, "Lunch", date(2026, 11, 11)
    )
    transaction2 = Transaction(
        200, transport, "Bus fare", date(2026, 11, 11)
    )

    assert food.name == "Food"
    assert str(food) == "Food"
    assert food == Category("food", "Other description")

    assert transaction1.amount == 500.0
    assert transaction1.category == food
    assert transaction1.description == "Lunch"
    assert transaction1.transaction_date == date(2026, 11, 11)

    assert transaction1 > transaction2
    assert transaction2 < transaction1
    assert transaction1 == Transaction(
        500, food, "Lunch", date(2026, 11, 11)
    )

    budget = Budget(food, 5000, 1500)

    assert budget.limit_amount == 5000.0
    assert budget.spent_amount == 1500.0
    assert budget.remaining_amount == 3500.0

    print("All basic assertions passed!")
    print(transaction1)
    print(transaction2)
    print(budget)
    print("Remaining:", budget.remaining_amount)


def check_raises(error_type, operation):
    """Check whether an operation raises the expected exception."""
    try:
        operation()
    except error_type:
        return
    except Exception as error:
        raise AssertionError(
            f"Expected {error_type.__name__}, "
            f"but got {type(error).__name__}"
        ) from error

    raise AssertionError(
        f"Expected {error_type.__name__}, but no error was raised"
    )


def run_validation_tests():
    """Test invalid inputs for the domain models."""

    food = Category("Food")

    check_raises(ValueError, lambda: Category(" "))
    check_raises(TypeError, lambda: Category(123))

    check_raises(
        ValueError,
        lambda: Transaction(0, food, "Lunch"),
    )
    check_raises(
        TypeError,
        lambda: Transaction(100, "Food", "Lunch"),
    )
    check_raises(
        ValueError,
        lambda: Transaction(100, food, " "),
    )

    check_raises(
        ValueError,
        lambda: Budget(food, -100),
    )
    check_raises(
        ValueError,
        lambda: Budget(food, 1000, -50),
    )

    print("All validation tests passed!")


if __name__ == "__main__":
    run_basic_assertions()
    run_validation_tests()
