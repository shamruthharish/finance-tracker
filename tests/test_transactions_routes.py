
import pytest
from datetime import date

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.database import CategoryDB, TransactionDB, User
from config import TestingConfig


@pytest.fixture
def app():
    """Create a Flask application with a temporary database."""

    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

        # Create a test category
        category = CategoryDB(name="Food")

        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("TestPassword123")
        )

        db.session.add_all([category, user])
        db.session.commit()

        yield app

        # Clean up the temporary database
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client and log in the test user."""

    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert response.status_code == 302

    return client


@pytest.fixture
def unauthenticated_client(app):
    """Create a client without logging in."""

    return app.test_client()


@pytest.fixture
def category_id(app):
    """Get the test category ID."""

    with app.app_context():
        category = db.session.execute(
            db.select(CategoryDB).where(
                CategoryDB.name == "Food"
            )
        ).scalar_one()

        return category.id



@pytest.fixture
def transaction_id(app, category_id):
    """Create a transaction for edit and delete tests."""

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(
                User.email == "test@example.com"
            )
        ).scalar_one()

        transaction = TransactionDB(
            user_id=user.id,
            amount=500,
            category_id=category_id,
            description="Test Lunch",
            transaction_date=date(2026, 11, 19),
            type="expense"
        )

        db.session.add(transaction)
        db.session.commit()

        return transaction.id



def test_transactions_page_loads(client):
    """Check whether the transactions page loads."""

    response = client.get("/transactions/")

    assert response.status_code == 200
    assert b"All Transactions" in response.data


def test_add_transaction(client, app, category_id):
    """Check whether a new transaction can be added."""

    response = client.post(
        "/transactions/add",
        data={
            "amount": "250",
            "category_id": str(category_id),
            "description": "Lunch",
            "transaction_date": "2026-11-19",
            "type": "expense"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Lunch" in response.data

    with app.app_context():
        transaction = db.session.execute(
            db.select(TransactionDB).where(
                TransactionDB.description == "Lunch"
            )
        ).scalar_one_or_none()

        assert transaction is not None
        assert transaction.amount == 250


def test_edit_transaction(client, app, transaction_id, category_id):
    """Check whether an existing transaction can be edited."""

    response = client.post(
        f"/transactions/edit/{transaction_id}",
        data={
            "amount": "750",
            "category_id": str(category_id),
            "description": "Updated Lunch",
            "transaction_date": "2026-11-19",
            "type": "expense"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Updated Lunch" in response.data

    with app.app_context():
        transaction = db.session.get(
            TransactionDB, transaction_id
        )

        assert transaction.amount == 750
        assert transaction.description == "Updated Lunch"


def test_delete_transaction(client, app, transaction_id):
    """Check whether a transaction can be deleted."""

    response = client.post(
        f"/transactions/delete/{transaction_id}",
        follow_redirects=True
    )

    assert response.status_code == 200

    with app.app_context():
        transaction = db.session.get(
            TransactionDB, transaction_id
        )

        assert transaction is None


def test_invalid_transaction_amount(client, app, category_id):
    """Check whether invalid amounts are rejected."""

    response = client.post(
        "/transactions/add",
        data={
            "amount": "-100",
            "category_id": str(category_id),
            "description": "Invalid Transaction",
            "transaction_date": "2026-11-19",
            "type": "expense"
        }
    )

    assert response.status_code == 200
    assert b"Amount must be a valid number" in response.data

    with app.app_context():
        transaction = db.session.execute(
            db.select(TransactionDB).where(
                TransactionDB.description == "Invalid Transaction"
            )
        ).scalar_one_or_none()

        assert transaction is None


def test_unauthenticated_user_redirected_to_login(
    unauthenticated_client
):
    """Check that unauthenticated users cannot access transactions."""

    response = unauthenticated_client.get("/transactions/")

    assert response.status_code == 302
    assert "/login" in response.location
