class OrderHistoryError(Exception):
    """Base error for order history operations."""


class AccessDeniedError(OrderHistoryError):
    """Raised when a requester cannot access the requested order data."""


class InvalidRequesterError(OrderHistoryError):
    """Raised when the requester profile is missing or invalid."""
