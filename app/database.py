
from pathlib import Path
from datetime import date

from sqlalchemy import (
    create_engine,
    Integer,
    Float,
    String,
    Date,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "finance_tracker.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Base class
class Base(DeclarativeBase):
    pass


# Transaction database model
class TransactionDB(Base):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    amount: Mapped[float] = mapped_column(Float)

    category: Mapped[str] = mapped_column(String(100))

    description: Mapped[str] = mapped_column(String(255))

    transaction_date: Mapped[date] = mapped_column(Date)

    type: Mapped[str] = mapped_column(String(20))


# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
