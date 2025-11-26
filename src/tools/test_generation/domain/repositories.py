"""Repository interfaces for test case generation."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .models import TestGenerationResult


class TestCaseRepository(ABC):
    """
    Abstract repository for test case generation operations.
    
    This interface defines the contract for generating test cases
    from swagger analysis results using ISTQB v4 techniques.
    """
    
    @abstractmethod
    async def generate_equivalence_partition_tests(
        self, 
        swagger_analysis: Dict[str, Any],
        endpoint_path: str = None,
        http_method: str = None
    ) -> List[TestGenerationResult]:
        """
        Generate test cases using Equivalence Partitioning technique.
        
        Args:
            swagger_analysis: Complete swagger analysis result (from JSON)
            endpoint_path: Optional - specific endpoint to generate tests for
            http_method: Optional - specific HTTP method to filter by
            
        Returns:
            List of TestGenerationResult, one per endpoint
            
        Raises:
            InvalidSwaggerAnalysisError: If analysis data is invalid
            PartitionIdentificationError: If partitions cannot be identified
        """
        pass