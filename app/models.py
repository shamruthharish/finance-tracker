
"""Domain models for the Finance Tracker."""

from datetime import date


class Category:
    """Represent a category used to classify financial transactions."""

    __slots__ = ("_name", "_description")

    def __init__(self, name, description=""):
        """Initialize a category with a name and optional description."""
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

        value = value.strip()

        if not value:
            raise ValueError("Category name cannot be empty")

        self._name = value

    @property
    def description(self):
        """Return the category description."""
        return self._description

    @description.setter
    def description(self, value):
        """Validate and update the category description."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")

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
        self, amount, category, description, transaction_date=None
    ):
        """Initialize a transaction after validating its information."""
        self.amount = amount
        self.category = category
        self.description = description
        self.transaction_date = (
            date.today() if transaction_date is None else transaction_date
        )

    @property
    def amount(self):
        """Return the transaction amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        """Validate and update the transaction amount."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Amount must be a number")

        if value <= 0:
            raise ValueError("Amount must be positive")

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

        value = value.strip()

        if not value:
            raise ValueError("Description cannot be empty")

        self._description = value

    @property
    def transaction_date(self):
        """Return the transaction date."""
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value):
        """Validate and update the transaction date."""
        if not isinstance(value, date):
            raise TypeError("Transaction date must be a date object")

        self._transaction_date = value

    @classmethod
    def create(cls, amount, category, description):
        """Create a transaction using today's date."""
        return cls(amount, category, description)

    def __str__(self):
        """Return a readable transaction representation."""
        return (
            f"{self.category} - ₹{self.amount:.2f} "
            f"({self.description})"
        )

    def __eq__(self, other):
        """Compare transactions by their financial details."""
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


def run_basic_assertions():
    """Run basic assertions to verify the domain models."""

    food = Category("Food", "Food expenses")
    travel = Category.from_name("Travel")

    assert food.name == "Food"
    assert food.description == "Food expenses"
    assert travel.name == "Travel"
    assert food == Category("food")

    t1 = Transaction(500, food, "Lunch")
    t2 = Transaction(200, travel, "Bus ticket")
    t3 = Transaction(500, food, "Lunch")

    assert t1.amount == 500.0
    assert t1.category == food
    assert t1.description == "Lunch"
    assert t1 == t3
    assert t2 < t1
    assert "Food" in str(t1)

    print("All basic assertions passed!")

def test_validation():
    """Check that invalid transaction and category data is rejected."""

    food = Category("Food")

    # Invalid category tests
    try:
        Category("")
        assert False, "Empty category should not be accepted"
    except ValueError:
        pass

    # Invalid amount test
    try:
        Transaction(-100, food, "Lunch")
        assert False, "Negative amount should not be accepted"
    except ValueError:
        pass

    # Invalid category type test
    try:
        Transaction(500, "Food", "Lunch")
        assert False, "String category should not be accepted"
    except TypeError:
        pass

    # Invalid description test
    try:
        Transaction(500, food, "")
        assert False, "Empty description should not be accepted"
    except ValueError:
        pass

    print("All validation tests passed!")


if __name__ == "__main__":
    run_basic_assertions()
    test_validation()
