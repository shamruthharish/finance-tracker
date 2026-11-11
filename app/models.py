import math
from datetime import date, datetime


class Category:
    __slots__ = ("_name", "_description")

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Category name cannot be empty.")
        self._name = value.strip()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise TypeError("Description must be a string.")
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

    __slots__ = (
        "_amount",
        "_category",
        "_description",
        "_transaction_date",
    )

    def __init__(self, amount, category, description, transaction_date=None):
        self.amount = amount
        self.category = category
        self.description = description
        self.transaction_date = (
            date.today() if transaction_date is None else transaction_date
        )

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Amount must be a number.")
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Amount must be a positive finite number.")
        self._amount = float(value)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, Category):
            raise TypeError("Category must be a Category object.")
        self._category = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Description cannot be empty.")
        self._description = value.strip()

    @property
    def transaction_date(self):
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value):
        if isinstance(value, datetime) or not isinstance(value, date):
            raise TypeError("Transaction date must be a date object.")
        self._transaction_date = value

    @classmethod
    def create(cls, amount, category_name, description):
        category = Category.from_name(category_name)
        return cls(amount, category, description)

    def __str__(self):
        return (
            f"{self.description}: {self.amount:.2f} "
            f"({self.category}) on {self.transaction_date}"
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
            raise TypeError("Category must be a Category object.")
        self._category = value

    @property
    def limit_amount(self):
        return self._limit_amount

    @limit_amount.setter
    def limit_amount(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Budget limit must be a number.")
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Budget limit must be positive.")
        self._limit_amount = float(value)

    @property
    def spent_amount(self):
        return self._spent_amount

    @spent_amount.setter
    def spent_amount(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Spent amount must be a number.")
        if not math.isfinite(value) or value < 0:
            raise ValueError("Spent amount cannot be negative.")
        self._spent_amount = float(value)

    @property
    def remaining_amount(self):
        return self.limit_amount - self.spent_amount

    @classmethod
    def create(cls, category_name, limit_amount):
        return cls(Category.from_name(category_name), limit_amount)

    def __str__(self):
        return (
            f"{self.category}: spent {self.spent_amount:.2f} "
            f"of {self.limit_amount:.2f}; "
            f"remaining {self.remaining_amount:.2f}"
        )
