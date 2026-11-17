
from models import Category, Transaction, Budget

food = Category("Food")
transport = Category("Transport")

t1 = Transaction(500, food, "Lunch")
t2 = Transaction(200, food, "Snacks")

budget = Budget(food, 2000, 700)

assert t1.amount == 500
assert t1.category == food
assert t1 < Transaction(800, food, "Dinner")
assert food == Category("food")
assert budget.remaining_amount == 1300

print("All Day 2 basic tests passed!")
print(t1)
print(budget)
# Validation tests

try:
    Transaction(-100, food, "Lunch")
except ValueError:
    print("Negative amount rejected successfully!")

try:
    Category("")
except ValueError:
    print("Empty category rejected successfully!")

try:
    Transaction(100, "Food", "Lunch")
except TypeError:
    print("Invalid category rejected successfully!")