"""Domain layer for Equivalence Partitioning technique (ISTQB v4)."""
from .models import (
    PartitionType,
    PartitionCategory,
    TestCasePriority,
    EquivalencePartition,
    TestCase,
    PartitionSet,
    TestGenerationResult
)
from .exceptions import (
    PartitionIdentificationError,
    TestCaseBuildError,
    InsufficientCoverageError,
    UnsupportedConstraintError
)
from .repositories import TestCaseRepository

__all__ = [
    "PartitionType",
    "PartitionCategory",
    "TestCasePriority",
    "EquivalencePartition",
    "TestCase",
    "PartitionSet",
    "TestGenerationResult",
    "PartitionIdentificationError",
    "TestCaseBuildError",
    "InsufficientCoverageError",
    "UnsupportedConstraintError",
    "TestCaseRepository"
]
