from datetime import date, datetime
import math

class Category: 

    __slots__ = ("_name", "_description")

    def __init__(self, name, description="General expenses"):
        self.name = name
        self.description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Category name must be a string")
        if not value.strip():
            raise ValueError("Category name cannot be empty")
        self._name = value.strip()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        if not value.strip():
            raise ValueError("Description cannot be empty")
        self._description = value.strip()

    @classmethod
    def from_name(cls, name):
        return cls(name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Category):
            return NotImplemented
        return self.name.casefold() == other.name.casefold()


class Transaction:
    __slots__ = ("_amount","_category","_description","_transaction_date",)

    def __init__(self,amount,category,description,transaction_date=None,):
        """Initialize a transaction after validating its details."""
        self.amount = amount
        self.category = category
        self.description = description

        if transaction_date is None:
            transaction_date = date.today()

        self.transaction_date = transaction_date

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Amount must be a number")

        if not math.isfinite(value):
            raise ValueError("Amount must be a finite number")

        if value <= 0:
            raise ValueError("Amount must be greater than zero")

        self._amount = float(value)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, Category):
            raise TypeError("Category must be a Category object")
        self._category = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        if not value.strip():
            raise ValueError("Description cannot be empty")
        self._description = value.strip()

    @property
    def transaction_date(self):
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value):
        if not isinstance(value, date) or isinstance(value, datetime):
            raise TypeError("Transaction date must be a date object")
        self._transaction_date = value

    @classmethod
    def create(cls, amount, category, description):
        return cls(amount, category, description)

    def __str__(self):
        return (
            f"{self.transaction_date} | "
            f"{self.category} | "
            f"{self.description} | "
            f"₹{self.amount:.2f}"
        )

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented

        return (
            self.amount == other.amount
            and self.category == other.category
            and self.description == other.description
            and self.transaction_date == other.transaction_date
        )

    def __lt__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.amount < other.amount


class Budget:

    __slots__ = ("_category", "_limit_amount", "_spent_amount")

    def __init__(self, category, limit_amount, spent_amount=0):
        self.category = category
        self.limit_amount = limit_amount
        self.spent_amount = spent_amount

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, Category):
            raise TypeError("Category must be a Category object")
        self._category = value

    @property
    def limit_amount(self):
        return self._limit_amount

    @limit_amount.setter
    def limit_amount(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Budget limit must be a number")
        if not math.isfinite(value):
            raise ValueError("Budget limit must be finite")
        if value <= 0:
            raise ValueError("Budget limit must be positive")
        self._limit_amount = float(value)

    @property
    def spent_amount(self):
        return self._spent_amount

    @spent_amount.setter
    def spent_amount(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Spent amount must be a number")
        if not math.isfinite(value):
            raise ValueError("Spent amount must be finite")
        if value < 0:
            raise ValueError("Spent amount cannot be negative")
        self._spent_amount = float(value)

    @property
    def remaining_amount(self):
        return self.limit_amount - self.spent_amount

    @classmethod
    def create(cls, category, limit_amount):
        return cls(category, limit_amount)

    def __str__(self):
        return (
            f"{self.category}: ₹{self.spent_amount:.2f} "
            f"spent out of ₹{self.limit_amount:.2f}"
        )


def run_basic_assertions():

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
