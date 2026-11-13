from contextlib import suppress

print("Program started")

with suppress(FileNotFoundError):
    number = int("hello")
    print(number)

print("Program continues!")