
from pathlib import Path
from datetime import date
from sqlalchemy import event
from flask_login import UserMixin

from sqlalchemy import (
    create_engine,
    Integer,
    Float,
    String,
    Date,
    ForeignKey,
    UniqueConstraint,
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
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Base class
class Base(DeclarativeBase):
    pass


class User(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )



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
    back_populates="category",
    cascade="all, delete-orphan",
    passive_deletes=True
)
    budgets: Mapped[list["BudgetDB"]] = relationship(
    back_populates="category",
    cascade="all, delete-orphan",
    passive_deletes=True
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
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )

    description: Mapped[str] = mapped_column(String(255))

    transaction_date: Mapped[date] = mapped_column(Date)

    type: Mapped[str] = mapped_column(String(20))

    # Many transactions belong to one category
    category: Mapped["CategoryDB"] = relationship(
        back_populates="transactions"
    )
# Budget database model
class BudgetDB(Base):

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    category_id: Mapped[int] = mapped_column(
    ForeignKey("categories.id", ondelete="CASCADE"),
    nullable=False
)

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    limit_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    category: Mapped["CategoryDB"] = relationship(
        back_populates="budgets"
    )

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "month",
            "year",
            name="unique_category_month_budget"
        ),
    )

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
