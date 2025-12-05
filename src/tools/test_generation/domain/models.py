"""Shared domain models for test generation (all techniques).

This module re-exports models from technique-specific subdirectories
to maintain backwards compatibility and provides unified models.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

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

# Re-export Boundary Value Analysis models
from .boundary_value_analysis.models import (
    BVAVersion,
    BoundaryType,
    BoundaryValue,
    BVATestCase,
    BVAResult
)


@dataclass
class UnifiedTestCase:
    """
    Unified test case model that works for all techniques.
    Respects Liskov Substitution Principle - can replace technique-specific models.
    """
    test_case_id: str
    test_name: str
    technique: str  # "Equivalence Partitioning", "Boundary Value Analysis (2-value)", etc.
    endpoint: str
    http_method: str
    test_data: Dict[str, Any]
    expected_status_code: int
    expected_result: str = ""
    expected_error: str = None
    priority: str = "medium"
    objective: str = ""
    preconditions: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Technique-specific data
    
    @classmethod
    def from_ep_test_case(cls, ep_case: TestCase) -> 'UnifiedTestCase':
        """Convert EP TestCase to UnifiedTestCase."""
        return cls(
            test_case_id=ep_case.test_case_id,
            test_name=ep_case.test_name,
            technique=ep_case.technique,
            endpoint=ep_case.endpoint,
            http_method=ep_case.http_method,
            test_data=ep_case.test_data,
            expected_status_code=ep_case.expected_status_code,
            expected_result=ep_case.expected_result,
            priority=ep_case.priority,
            objective=ep_case.objective,
            preconditions=ep_case.preconditions,
            steps=ep_case.steps,
            tags=ep_case.tags,
            metadata={"partitions_covered": ep_case.partitions_covered}
        )
    
    @classmethod
    def from_bva_test_case(cls, bva_case: BVATestCase) -> 'UnifiedTestCase':
        """Convert BVA TestCase to UnifiedTestCase."""
        return cls(
            test_case_id=bva_case.test_case_id,
            test_name=bva_case.test_name,
            technique=f"Boundary Value Analysis ({bva_case.bva_version})",
            endpoint=bva_case.endpoint,
            http_method=bva_case.http_method,
            test_data=bva_case.test_data,
            expected_status_code=bva_case.expected_status_code,
            expected_error=bva_case.expected_error,
            priority=bva_case.priority,
            tags=["bva", bva_case.bva_version.replace("-", "_")],
            metadata={"boundary_info": bva_case.boundary_info}
        )
    
    @classmethod
    def from_dt_test_case(cls, dt_case) -> 'UnifiedTestCase':
        """Convert Decision Table TestCase to UnifiedTestCase."""
        return cls(
            test_case_id=dt_case.test_case_id,
            test_name=dt_case.test_name,
            technique="Decision Table",
            endpoint=dt_case.endpoint,
            http_method=dt_case.http_method,
            test_data=dt_case.test_data,
            expected_status_code=dt_case.expected_status_code,
            expected_error=dt_case.expected_error,
            priority=dt_case.priority,
            objective=dt_case.objective,
            tags=dt_case.tags,
            metadata={
                "rule_id": dt_case.rule_id,
                "condition_summary": dt_case.condition_summary,
                "action_summary": dt_case.action_summary
            }
        )


@dataclass
class UnifiedTestResult:
    """
    Unified result containing test cases from multiple techniques.
    Respects Single Responsibility: only holds and organizes results.
    """
    endpoint: str
    http_method: str
    techniques_applied: List[str] = field(default_factory=list)
    test_cases: List[UnifiedTestCase] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_ep_result(self, ep_result: TestGenerationResult):
        """Add EP results to unified result."""
        self.techniques_applied.append("Equivalence Partitioning")
        for tc in ep_result.test_cases:
            self.test_cases.append(UnifiedTestCase.from_ep_test_case(tc))
        
        self.metadata["ep_metrics"] = {
            "total_partitions": ep_result.total_partitions,
            "valid_partitions": ep_result.valid_partitions,
            "invalid_partitions": ep_result.invalid_partitions,
            "coverage_percentage": ep_result.coverage_percentage
        }
    
    def add_bva_result(self, bva_result: BVAResult):
        """Add BVA results to unified result."""
        technique_name = f"Boundary Value Analysis ({bva_result.bva_version})"
        self.techniques_applied.append(technique_name)
        
        for tc in bva_result.test_cases:
            self.test_cases.append(UnifiedTestCase.from_bva_test_case(tc))
        
        version_key = f"bva_{bva_result.bva_version}_metrics"
        self.metadata[version_key] = {
            "boundaries_identified": bva_result.boundaries_identified,
            "coverage_percentage": bva_result.coverage_percentage,
            "coverage_items_tested": bva_result.coverage_items_tested,
            "coverage_items_total": bva_result.coverage_items_total
        }
    
    def add_dt_result(self, dt_result):
        """Add Decision Table results to unified result."""
        self.techniques_applied.append("Decision Table")
        
        for tc in dt_result.test_cases:
            self.test_cases.append(UnifiedTestCase.from_dt_test_case(tc))
        
        self.metadata["decision_table_metrics"] = dt_result.metrics
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "total_test_cases": len(self.test_cases),
            "techniques_applied": self.techniques_applied,
            **self.metadata
        }


__all__ = [
    # EP models (backwards compatibility)
    "PartitionType",
    "PartitionCategory",
    "TestCasePriority",
    "EquivalencePartition",
    "TestCase",
    "PartitionSet",
    "TestGenerationResult",
    # BVA models
    "BVAVersion",
    "BoundaryType",
    "BoundaryValue",
    "BVATestCase",
    "BVAResult",
    # Unified models
    "UnifiedTestCase",
    "UnifiedTestResult"
]