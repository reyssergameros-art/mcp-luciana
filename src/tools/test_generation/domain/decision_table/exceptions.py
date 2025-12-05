"""Exceptions for Decision Table test generation (ISTQB v4)."""


class DecisionTableError(Exception):
    """Base exception for Decision Table test generation errors."""
    pass


class InvalidRuleError(DecisionTableError):
    """Raised when a decision rule is invalid or inconsistent."""
    pass


class InfeasibleCombinationError(DecisionTableError):
    """Raised when a combination of conditions is not feasible (N/A)."""
    pass
