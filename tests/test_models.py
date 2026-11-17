
import pytest
from datetime import date

from app.models import Category, Transaction, Budget


@pytest.fixture
def food():
    return Category("Food")


@pytest.fixture
def transaction(food):
    return Transaction(500, food, "Lunch")


# CATEGORY TESTS

def test_category_name(food):
    assert food.name == "Food"


def test_category_empty_name():
    with pytest.raises(ValueError):
        Category("")


def test_category_invalid_type():
    with pytest.raises(ValueError):
        Category(123)


def test_category_case_insensitive():
    assert Category("Food") == Category("food")


def test_category_description():
    category = Category("Food", "Daily meals")
    assert category.description == "Daily meals"


# TRANSACTION TESTS

def test_transaction_amount(transaction):
    assert transaction.amount == 500.0


def test_transaction_description(transaction):
    assert transaction.description == "Lunch"


def test_transaction_category(transaction, food):
    assert transaction.category == food


def test_transaction_negative_amount(food):
    with pytest.raises(ValueError):
        Transaction(-100, food, "Lunch")


def test_transaction_zero_amount(food):
    with pytest.raises(ValueError):
        Transaction(0, food, "Lunch")


def test_transaction_invalid_amount_type(food):
    with pytest.raises(TypeError):
        Transaction("500", food, "Lunch")


def test_transaction_invalid_category():
    with pytest.raises(TypeError):
        Transaction(500, "Food", "Lunch")


def test_transaction_empty_description(food):
    with pytest.raises(ValueError):
        Transaction(500, food, "")


def test_transaction_invalid_date(food):
    with pytest.raises(TypeError):
        Transaction(500, food, "Lunch", "2026-11-17")


def test_transaction_comparison(food):
    first = Transaction(500, food, "Lunch")
    second = Transaction(800, food, "Dinner")

    assert first < second


# BUDGET TESTS

def test_budget_remaining(food):
    budget = Budget(food, 2000, 700)
    assert budget.remaining_amount == 1300


def test_budget_invalid_limit(food):
    with pytest.raises(ValueError):
        Budget(food, -1000)


def test_budget_negative_spending(food):
    with pytest.raises(ValueError):
        Budget(food, 2000, -100)


def test_budget_invalid_category():
    with pytest.raises(TypeError):
        Budget("Food", 2000)
def test_budget_exceeded(food):
    budget = Budget(food, 2000, 2500)
    assert budget.is_exceeded is True


def test_budget_not_exceeded(food):
    budget = Budget(food, 2000, 1500)
    assert budget.is_exceeded is False