
import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        print(f"execution time: {end - start:.6f} seconds")
        return result

    return wrapper


def validate_input(func):
    @wraps(func)
    def wrapper(amount, *args, **kwargs):
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError("amount must be a number")

        if amount <= 0:
            raise ValueError("amount must be greater than 0")

        return func(amount, *args, **kwargs)

    return wrapper


def validate_amount(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from inspect import signature

        bound = signature(func).bind(*args, **kwargs)
        amount = bound.arguments["amount"]

        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")

        if amount <= 0:
            raise ValueError("amount must be greater than zero")

        return func(*args, **kwargs)

    return wrapper


# Day 3 demonstrations
if __name__ == "__main__":

    @timer
    def calculate_sum():
        return sum(range(1_000_000))

    print("Result:", calculate_sum())

    @validate_input
    def add_expense(amount):
        print(f"Expense added: ₹{amount}")

    add_expense(500)

    try:
        add_expense(-200)
    except ValueError as error:
        print("Validation Error:", error)
