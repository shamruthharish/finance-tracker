class TransactionError(Exception):
    """Base exception for Finance Tracker."""
    pass


class InvalidAmountError(TransactionError):
    """Raised when a transaction amount is invalid."""
    pass


class InvalidCategoryError(TransactionError):
    """Raised when a category is invalid."""
    pass


class TransactionNotFoundError(TransactionError):
    """Raised when a transaction cannot be found."""
    pass


class InvalidTransactionDataError(TransactionError):
    """Raised when transaction data is invalid."""
    pass


class CSVImportError(TransactionError):
    """Raised when CSV import fails."""
    pass