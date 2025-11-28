"""Shared repository interfaces for test generation (all techniques).

This module re-exports repository interfaces from technique-specific subdirectories
to maintain backwards compatibility.
"""

# Re-export Equivalence Partitioning repository for backwards compatibility
from .equivalence_partitioning.repositories import TestCaseRepository

__all__ = ["TestCaseRepository"]