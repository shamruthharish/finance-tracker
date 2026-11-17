
from datetime import date

from sqlalchemy import select

from app.database import SessionLocal, TransactionDB


# CREATE, READ, UPDATE, DELETE
with SessionLocal() as session:

    # CREATE
    transaction = TransactionDB(
        amount=500,
        category="Food",
        description="Day 7 CRUD Demo",
        transaction_date=date.today(),
        type="expense"
    )

    session.add(transaction)
    session.commit()

    demo_id = transaction.id
    print("CREATE: Transaction added!", demo_id)

    # READ
    result = session.scalar(
        select(TransactionDB).where(
            TransactionDB.id == demo_id
        )
    )

    print("READ:", result.description, result.amount)

    # UPDATE
    result.amount = 600
    session.commit()

    print("UPDATE: New amount =", result.amount)

    # DELETE
    session.delete(result)
    session.commit()

    print("DELETE: Demo transaction removed!")
