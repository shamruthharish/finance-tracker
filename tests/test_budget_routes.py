
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from config import TestingConfig
from app.extensions import db
from app.database import BudgetDB, CategoryDB, User


@pytest.fixture
def app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

        food = CategoryDB(name="Food")
        travel = CategoryDB(name="Travel")

        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("TestPassword123")
        )

        db.session.add_all([food, travel, user])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 302

    return client


@pytest.fixture
def category_id(app):
    with app.app_context():
        category = db.session.execute(
            db.select(CategoryDB).where(
                CategoryDB.name == "Food"
            )
        ).scalar_one()

        return category.id


def test_budget_page_loads(client):
    response = client.get("/budgets/")

    assert response.status_code == 200
    assert b"Monthly Budgets" in response.data


def test_add_budget(client, app, category_id):
    response = client.post(
        "/budgets/add",
        data={
            "category_id": category_id,
            "month": 11,
            "year": 2026,
            "limit_amount": "3000"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Budget added successfully!" in response.data

    with app.app_context():
        budget = db.session.execute(
            db.select(BudgetDB)
        ).scalar_one()

        assert budget.limit_amount == 3000
        assert budget.month == 11
        assert budget.year == 2026
        assert budget.user_id == 1


def test_invalid_budget_amount(client, category_id):
    response = client.post(
        "/budgets/add",
        data={
            "category_id": category_id,
            "month": 11,
            "year": 2026,
            "limit_amount": "-500"
        }
    )

    assert response.status_code == 200
    assert b"Budget amount must be greater than zero." in response.data


def test_duplicate_budget(client, category_id):
    data = {
        "category_id": category_id,
        "month": 11,
        "year": 2026,
        "limit_amount": "3000"
    }

    client.post("/budgets/add", data=data)

    response = client.post("/budgets/add", data=data)

    assert response.status_code == 200
    assert b"A budget already exists" in response.data


def test_invalid_category(client):
    response = client.post(
        "/budgets/add",
        data={
            "category_id": 9999,
            "month": 11,
            "year": 2026,
            "limit_amount": "3000"
        }
    )

    assert response.status_code == 200
    assert b"Selected category does not exist." in response.data
