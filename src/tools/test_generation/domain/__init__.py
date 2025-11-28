"""Domain layer for test generation (all ISTQB v4 techniques).

This module provides a unified interface to all testing techniques while
maintaining clean separation through subdirectories.

Architecture:
- Shared exceptions and base classes in root
- Technique-specific models in subdirectories (equivalence_partitioning/, boundary_value_analysis/)
- Re-exports for backwards compatibility and simplified imports
"""

# Shared base exceptions
from .exceptions import TestGenerationError, InvalidSwaggerAnalysisError

# Re-export Equivalence Partitioning (for backwards compatibility)
from .models import (
    PartitionType,
    PartitionCategory,
    TestCasePriority,
    EquivalencePartition,
    TestCase,
    PartitionSet,
    TestGenerationResult
)

__all__ = [
    # Shared exceptions
    "TestGenerationError",
    "InvalidSwaggerAnalysisError",
    # EP models (re-exported)
    "PartitionType",
    "PartitionCategory",
    "TestCasePriority",
    "EquivalencePartition",
    "TestCase",
    "PartitionSet",
    "TestGenerationResult"
]