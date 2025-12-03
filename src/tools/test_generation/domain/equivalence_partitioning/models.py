"""Domain models for Equivalence Partitioning technique (ISTQB v4)."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class PartitionType(Enum):
    """Type of equivalence partition."""
    VALID = "valid"
    INVALID = "invalid"


class PartitionCategory(Enum):
    """Category of partition based on constraint type."""
    LENGTH = "length"  # min_length, max_length
    RANGE = "range"  # minimum, maximum for numeric values
    FORMAT = "format"  # uuid, email, date, etc.
    ENUM = "enum"  # specific set of allowed values
    PATTERN = "pattern"  # regex pattern
    REQUIRED = "required"  # field presence
    TYPE = "type"  # data type validation


class TestCasePriority(Enum):
    """Priority level for test cases."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class EquivalencePartition:
    """
    Represents an equivalence partition for test case generation.
    
    According to ISTQB v4, an equivalence partition divides data into partitions
    where all elements should be processed the same way by the test object.
    """
    partition_id: str  # Unique identifier for the partition
    partition_type: PartitionType  # VALID or INVALID
    category: PartitionCategory  # Type of constraint being tested
    field_name: str  # Name of the field being tested
    description: str  # Human-readable description of the partition
    test_value: Any  # Representative value from this partition
    constraint_details: Dict[str, Any]  # Details about the constraint
    rationale: str  # Why this partition exists (ISTQB requirement)
    
    def __post_init__(self):
        """Validate partition data."""
        if not self.partition_id:
            raise ValueError("partition_id cannot be empty")
        if not self.field_name:
            raise ValueError("field_name cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")


@dataclass
class TestCase:
    """
    Represents a test case generated using equivalence partitioning technique.
    
    Each test case exercises at least one partition from each partition set,
    following ISTQB v4 "Each Choice Coverage" criterion.
    """
    test_case_id: str  # Unique identifier
    test_name: str  # Descriptive name
    technique: str  # ISTQB technique used (e.g., "Equivalence Partitioning")
    endpoint: str  # API endpoint being tested
    http_method: str  # HTTP method (GET, POST, etc.)
    priority: TestCasePriority  # Test priority
    objective: str  # What the test aims to verify
    partitions_covered: List[EquivalencePartition]  # Partitions exercised by this test
    test_data: Dict[str, Any]  # Actual test data to use
    expected_result: str  # Expected outcome
    expected_status_code: int  # Expected HTTP status code
    expected_error: Optional[str] = None  # Expected error code for negative tests
    preconditions: List[str] = field(default_factory=list)  # Conditions before test
    steps: List[str] = field(default_factory=list)  # Test execution steps
    tags: List[str] = field(default_factory=list)  # Tags for categorization
    
    def __post_init__(self):
        """Validate test case data."""
        if not self.test_case_id:
            raise ValueError("test_case_id cannot be empty")
        if not self.test_name:
            raise ValueError("test_name cannot be empty")
        if not self.endpoint:
            raise ValueError("endpoint cannot be empty")
        # partitions_covered can be empty for status code coverage tests
        # which don't test specific partitions but HTTP response codes


@dataclass
class PartitionSet:
    """
    Represents a set of partitions for a specific field or parameter.
    
    Each field may have multiple partitions (e.g., valid range, below minimum, above maximum).
    """
    field_name: str  # Field or parameter name
    field_type: str  # Data type (string, integer, etc.)
    partitions: List[EquivalencePartition]  # All partitions for this field
    
    def get_valid_partitions(self) -> List[EquivalencePartition]:
        """Return only valid partitions."""
        return [p for p in self.partitions if p.partition_type == PartitionType.VALID]
    
    def get_invalid_partitions(self) -> List[EquivalencePartition]:
        """Return only invalid partitions."""
        return [p for p in self.partitions if p.partition_type == PartitionType.INVALID]


@dataclass
class TestGenerationResult:
    """
    Result of test case generation using equivalence partitioning.
    
    Contains all generated test cases and coverage metrics.
    """
    endpoint: str
    http_method: str
    technique: str  # ISTQB technique used
    total_partitions: int  # Total number of partitions identified
    valid_partitions: int  # Number of valid partitions
    invalid_partitions: int  # Number of invalid partitions
    partition_sets: List[PartitionSet]  # All partition sets
    test_cases: List[TestCase]  # Generated test cases
    coverage_percentage: float  # Partition coverage achieved
    summary: str  # Human-readable summary
    
    def __post_init__(self):
        """Calculate coverage if not provided."""
        if self.coverage_percentage == 0 and self.total_partitions > 0:
            covered_partitions = set()
            for test_case in self.test_cases:
                for partition in test_case.partitions_covered:
                    covered_partitions.add(partition.partition_id)
            self.coverage_percentage = (len(covered_partitions) / self.total_partitions) * 100
