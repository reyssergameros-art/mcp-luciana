"""Domain models for Boundary Value Analysis (ISTQB v4)."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class BVAVersion(Enum):
    """BVA technique version according to ISTQB v4."""
    TWO_VALUE = "2-value"  # Boundary + 1 neighbor per side
    THREE_VALUE = "3-value"  # Boundary + 2 neighbors per side


class BoundaryType(Enum):
    """Type of boundary value."""
    MINIMUM = "minimum"
    MAXIMUM = "maximum"


@dataclass
class BoundaryValue:
    """Represents a boundary value with its neighbors."""
    field_name: str
    field_type: str
    boundary_type: BoundaryType
    boundary_value: Any
    lower_neighbor: Optional[Any] = None
    upper_neighbor: Optional[Any] = None
    constraint_type: str = ""
    
    def get_test_values_2value(self) -> List[Any]:
        """Get test values for 2-value BVA."""
        values = [self.boundary_value]
        if self.boundary_type == BoundaryType.MINIMUM and self.lower_neighbor is not None:
            values.append(self.lower_neighbor)
        elif self.boundary_type == BoundaryType.MAXIMUM and self.upper_neighbor is not None:
            values.append(self.upper_neighbor)
        return values
    
    def get_test_values_3value(self) -> List[Any]:
        """Get test values for 3-value BVA."""
        values = [self.boundary_value]
        if self.lower_neighbor is not None:
            values.insert(0, self.lower_neighbor)
        if self.upper_neighbor is not None:
            values.append(self.upper_neighbor)
        return values


@dataclass
class BVATestCase:
    """Represents a BVA test case."""
    test_case_id: str
    test_name: str
    endpoint: str
    http_method: str
    test_data: Dict[str, Any]
    expected_status_code: int
    expected_error: Optional[str] = None
    boundary_info: Optional[Dict[str, Any]] = None
    bva_version: str = "2-value"
    priority: str = "medium"


@dataclass
class BVAResult:
    """Results of BVA test generation for an endpoint."""
    endpoint: str
    http_method: str
    bva_version: str
    boundaries_identified: int
    test_cases: List[BVATestCase] = field(default_factory=list)
    coverage_percentage: float = 0.0
    coverage_items_tested: int = 0
    coverage_items_total: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_coverage(self):
        """Calculate BVA coverage percentage."""
        if self.coverage_items_total == 0:
            self.coverage_percentage = 0.0
            return
        
        self.coverage_percentage = (self.coverage_items_tested / self.coverage_items_total) * 100
