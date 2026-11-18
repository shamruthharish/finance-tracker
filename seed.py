
from app.database import (
    SessionLocal,
    CategoryDB,
    BudgetDB,
)


def seed_data():
    session = SessionLocal()

    try:
        # Sample categories
        category_names = [
            "Food",
            "Travel",
            "Shopping",
            "Entertainment",
        ]

        for name in category_names:
            category = session.query(CategoryDB).filter_by(
                name=name
            ).first()

            if category is None:
                session.add(CategoryDB(name=name))

        session.flush()

        # Sample monthly budgets
        sample_budgets = {
            "Food": 1000,
            "Travel": 2000,
            "Shopping": 1500,
            "Entertainment": 800,
        }

        for name, limit in sample_budgets.items():
            category = session.query(CategoryDB).filter_by(
                name=name
            ).first()

            existing_budget = session.query(BudgetDB).filter_by(
                category_id=category.id,
                month=11,
                year=2026,
            ).first()

            if existing_budget is None:
                session.add(
                    BudgetDB(
                        category_id=category.id,
                        month=11,
                        year=2026,
                        limit_amount=limit,
                    )
                )

        session.commit()
        print("Seed data inserted successfully!")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
