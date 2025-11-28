"""Domain exceptions for Equivalence Partitioning technique."""
from ..exceptions import TestGenerationError


class PartitionIdentificationError(TestGenerationError):
    """
    Raised when partitions cannot be identified from constraints.
    
    Use this when:
    - Constraint data is malformed
    - Unable to determine valid/invalid boundaries
    - Conflicting constraint definitions
    
    Example:
        raise PartitionIdentificationError("Cannot determine range for field 'age'")
    """
    pass


class TestCaseBuildError(TestGenerationError):
    """
    Raised when test case construction fails.
    
    Use this when:
    - Cannot generate representative test values
    - Missing required partition data
    - Invalid test case configuration
    
    Example:
        raise TestCaseBuildError("Cannot generate test value for UUID format")
    """
    pass


class InsufficientCoverageError(TestGenerationError):
    """
    Raised when generated tests don't achieve minimum coverage.
    
    Use this when:
    - Not all partitions are covered by test cases
    - Coverage percentage below threshold
    - Missing critical test scenarios
    
    Example:
        raise InsufficientCoverageError("Only 60% partition coverage achieved, minimum is 80%")
    """
    pass


class UnsupportedConstraintError(TestGenerationError):
    """
    Raised when encountering unsupported constraint types.
    
    Use this when:
    - Constraint type not yet implemented
    - Format not recognized
    - Complex validation rules beyond current scope
    
    Example:
        raise UnsupportedConstraintError("Custom regex patterns not yet supported")
    """
    pass
