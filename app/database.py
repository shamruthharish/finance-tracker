
from pathlib import Path
from datetime import date

from sqlalchemy import (
    create_engine,
    Integer,
    Float,
    String,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
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


# Category database model
class CategoryDB(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    # One category can have many transactions
    transactions: Mapped[list["TransactionDB"]] = relationship(
        back_populates="category"
    )


# Transaction database model
class TransactionDB(Base):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    amount: Mapped[float] = mapped_column(Float)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    description: Mapped[str] = mapped_column(String(255))

    transaction_date: Mapped[date] = mapped_column(Date)

    type: Mapped[str] = mapped_column(String(20))

    # Many transactions belong to one category
    category: Mapped["CategoryDB"] = relationship(
        back_populates="transactions"
    )


# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
