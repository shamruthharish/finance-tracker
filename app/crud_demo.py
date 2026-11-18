
from datetime import date
from sqlalchemy import select

from app.database import SessionLocal, TransactionDB, CategoryDB


with SessionLocal() as session:

    # Find the Food category
    category = session.scalar(
        select(CategoryDB).where(CategoryDB.name == "Food")
    )

    # Create it only if it does not exist
    if category is None:
        category = CategoryDB(name="Food")
        session.add(category)
        session.flush()

    # CREATE
    transaction = TransactionDB(
        amount=500,
        category=category,
        description="Day 8 CRUD Demo",
        transaction_date=date.today(),
        type="expense"
    )

    session.add(transaction)
    session.commit()

    demo_id = transaction.id
    print("CREATE: Transaction added!", demo_id)

    # READ
    result = session.scalar(
        select(TransactionDB).where(TransactionDB.id == demo_id)
    )

    print(
        "READ:",
        result.description,
        result.amount,
        result.category.name
    )

    # UPDATE
    result.amount = 600
    session.commit()

    print("UPDATE: New amount =", result.amount)

    # DELETE only the demo transaction
    session.delete(result)
    session.commit()

    print("DELETE: Demo transaction removed!")
