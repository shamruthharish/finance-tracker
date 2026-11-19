class TransactionError(Exception):
    """Base exception for Finance Tracker."""
    pass


class InvalidAmountError(TransactionError):
    """Raised when transaction amount is invalid."""
    pass


class InvalidCategoryError(TransactionError):
    """Raised when transaction category is invalid."""
    pass


class TransactionNotFoundError(TransactionError):
    """Raised when a transaction cannot be found."""
    pass


class InvalidTransactionDataError(TransactionError):
    """Raised when transaction data is invalid."""
    pass

class BudgetExceededError(Exception):
    """Raised when monthly spending exceeds the budget."""
    pass

class CSVImportError(TransactionError):
    """Raised when CSV import fails."""
    pass

class CSVImportError(TransactionError):
    """Raised when CSV import fails."""
    pass