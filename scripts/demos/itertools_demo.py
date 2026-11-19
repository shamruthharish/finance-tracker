"""from itertools import count

for number in count(1):
    print(number)

    if number == 5:
        break
from itertools import cycle

colors = cycle(["Red", "Green", "Blue"])

for i in range(6):
    print(next(colors))"""

from itertools import chain

food = ["Rice", "Burger"]
travel = ["Bus", "Train"]

combined = chain(food, travel)

for item in combined:
    print(item)