"""Domain models and exceptions for Decision Table technique (ISTQB v4)."""

from .models import (
    ConditionType,
    ConditionValue,
    ActionValue,
    DecisionCondition,
    DecisionAction,
    DecisionRule,
    DecisionTable,
    DecisionTableResult,
    DecisionTableTestCase
)
from .exceptions import (
    DecisionTableError,
    InvalidRuleError,
    InfeasibleCombinationError
)

__all__ = [
    # Enums
    "ConditionType",
    "ConditionValue",
    "ActionValue",
    # Models
    "DecisionCondition",
    "DecisionAction",
    "DecisionRule",
    "DecisionTable",
    "DecisionTableResult",
    "DecisionTableTestCase",
    # Exceptions
    "DecisionTableError",
    "InvalidRuleError",
    "InfeasibleCombinationError"
]
