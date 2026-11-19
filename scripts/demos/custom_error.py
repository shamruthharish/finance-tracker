class InvalidAmountError(Exception):
    pass


try:
    amount = -500

    if amount <= 0:
        raise InvalidAmountError("Amount must be greater than zero")

except InvalidAmountError as e:
    print("Error:", e)