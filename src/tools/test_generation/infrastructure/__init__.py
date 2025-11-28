"""Infrastructure layer for test generation (all ISTQB v4 techniques).

This module provides infrastructure components organized by testing technique:
- equivalence_partitioning/: EP-specific implementations
- boundary_value_analysis/: BVA-specific implementations

Each subdirectory contains complete infrastructure for its technique following
Clean Architecture and SOLID principles.
"""

# Infrastructure is now organized by technique in subdirectories
# Import from specific subdirectories as needed:
# - from .equivalence_partitioning.partition_identifier import PartitionIdentifierRefactored
# - from .boundary_value_analysis.boundary_identifier import BoundaryIdentifier

__all__ = []