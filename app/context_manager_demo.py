class OperationContext:

    def __init__(self, operation):
        self.operation = operation

    def __enter__(self):
        print(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type:
            print(f"Error occurred: {exc_value}")
        else:
            print("Operation completed successfully!")

        return False


with OperationContext("Adding transaction"):
    print("Transaction is being added...")


try:
    with OperationContext("Processing payment"):
        print("Processing...")
        raise ValueError("Invalid payment amount")

except ValueError as error:
    print(f"Handled error: {error}")