"""Shared domain models for test generation (all techniques).

This module re-exports models from technique-specific subdirectories
to maintain backwards compatibility.
"""

# Re-export Equivalence Partitioning models for backwards compatibility
from .equivalence_partitioning.models import (
    PartitionType,
    PartitionCategory,
    TestCasePriority,
    EquivalencePartition,
    TestCase,
    PartitionSet,
    TestGenerationResult
)

__all__ = [
    "PartitionType",
    "PartitionCategory",
    "TestCasePriority",
    "EquivalencePartition",
    "TestCase",
    "PartitionSet",
    "TestGenerationResult"
]