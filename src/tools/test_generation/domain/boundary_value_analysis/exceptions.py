"""Exceptions for Boundary Value Analysis."""


class BVAError(Exception):
    """Base exception for BVA errors."""
    pass


class InvalidBoundaryError(BVAError):
    """Raised when boundary values cannot be determined."""
    pass


class UnsupportedTypeError(BVAError):
    """Raised when data type doesn't support BVA (not ordered)."""
    pass
