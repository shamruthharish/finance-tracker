
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from app.database import Base, CategoryDB, TransactionDB, User
from app.reports import category_summary


@pytest.fixture
def test_session():

    # Create a separate temporary database for testing
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:

        food = CategoryDB(name="Food")
        shopping = CategoryDB(name="Shopping")
        travel = CategoryDB(name="Travel")
        salary = CategoryDB(name="Salary")

        user = User(
            username="reportuser",
            email="report@example.com",
            password_hash=generate_password_hash("TestPassword123")
        )

        session.add_all([food, shopping, travel, salary, user])
        session.commit()

        transactions = [
            TransactionDB(
                user_id=user.id,
                amount=150,
                category=food,
                description="Snacks",
                transaction_date=date(2026, 11, 10),
                type="expense"
            ),
            TransactionDB(
                user_id=user.id,
                amount=500,
                category=food,
                description="Lunch",
                transaction_date=date(2026, 11, 12),
                type="expense"
            ),
            TransactionDB(
                user_id=user.id,
                amount=750,
                category=shopping,
                description="Clothes",
                transaction_date=date(2026, 11, 13),
                type="expense"
            ),
            TransactionDB(
                user_id=user.id,
                amount=300,
                category=travel,
                description="Bus Ticket",
                transaction_date=date(2026, 11, 14),
                type="expense"
            ),
            TransactionDB(
                user_id=user.id,
                amount=2000,
                category=salary,
                description="Monthly Salary",
                transaction_date=date(2026, 11, 15),
                type="income"
            ),
            TransactionDB(
                user_id=user.id,
                amount=900,
                category=shopping,
                description="December Shopping",
                transaction_date=date(2026, 12, 5),
                type="expense"
            )
        ]

        session.add_all(transactions)
        session.commit()

        yield session

    engine.dispose()


def test_category_summary_sorted(test_session):

    result = category_summary(
        year=2026,
        month=11,
        session=test_session
    )

    assert result == [
        {"category": "Shopping", "total": 750.0},
        {"category": "Food", "total": 650.0},
        {"category": "Travel", "total": 300.0}
    ]


def test_category_summary_excludes_income(test_session):

    result = category_summary(
        year=2026,
        month=11,
        session=test_session
    )

    categories = [item["category"] for item in result]

    assert "Salary" not in categories


def test_category_summary_excludes_other_month(test_session):

    result = category_summary(
        year=2026,
        month=11,
        session=test_session
    )

    assert all(
        item["total"] != 1650.0
        for item in result
    )


def test_category_summary_limit(test_session):

    result = category_summary(
        year=2026,
        month=11,
        limit=2,
        session=test_session
    )

    assert len(result) == 2
    assert result[0]["category"] == "Shopping"


def test_category_summary_invalid_month(test_session):

    with pytest.raises(ValueError):
        category_summary(
            year=2026,
            month=13,
            session=test_session
        )


def test_category_summary_invalid_limit(test_session):

    with pytest.raises(ValueError):
        category_summary(
            year=2026,
            month=11,
            limit=0,
            session=test_session
        )
