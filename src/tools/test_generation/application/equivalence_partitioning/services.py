"""Application service for Equivalence Partitioning technique (ISTQB v4)."""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

from ...domain.models import TestGenerationResult, PartitionSet, TestCase
from ...domain.exceptions import InvalidSwaggerAnalysisError, TestGenerationError
from src.shared.utils.file_operations import FileOperations
from ...infrastructure.equivalence_partitioning.partition_identifier import PartitionIdentifierRefactored
from ...infrastructure.equivalence_partitioning.test_case_builder import TestCaseBuilderRefactored
from ...infrastructure.equivalence_partitioning.status_code_resolver import StatusCodeResolver
from ...infrastructure.equivalence_partitioning.error_code_resolver import ErrorCodeResolver
from src.shared.config import SwaggerConstants


class EquivalencePartitionService:
    """
    Refactored application service following SOLID principles.
    
    Improvements:
    - Dependency Injection: Injects resolvers into builder
    - Single Responsibility: Orchestrates but delegates specific tasks
    - Open/Closed: Easy to swap implementations without changing this class
    
    Orchestrates the test generation process:
    1. Load swagger analysis from JSON file
    2. Identify equivalence partitions for each field using specialized generators
    3. Build test cases with dynamic status/error code resolution
    4. Calculate coverage metrics
    """
    
    def __init__(self):
        """Initialize service with refactored components."""
        # Use refactored implementations
        self.partition_identifier = PartitionIdentifierRefactored()
        
        # Create resolvers
        self.status_resolver = StatusCodeResolver()
        self.error_resolver = ErrorCodeResolver()
        
        # Inject resolvers into builder (Dependency Injection)
        self.test_case_builder = TestCaseBuilderRefactored(
            status_resolver=self.status_resolver,
            error_resolver=self.error_resolver
        )
    
    async def generate_test_cases_from_json(
        self,
        swagger_analysis_file: str,
        endpoint_filter: Optional[str] = None,
        method_filter: Optional[str] = None
    ) -> List[TestGenerationResult]:
        """
        Generate test cases from swagger analysis JSON file.
        
        Args:
            swagger_analysis_file: Path to swagger analysis JSON output
            endpoint_filter: Optional - filter by specific endpoint
            method_filter: Optional - filter by HTTP method
            
        Returns:
            List of TestGenerationResult, one per endpoint
            
        Raises:
            InvalidSwaggerAnalysisError: If JSON is invalid or missing data
            TestGenerationError: If test generation fails
        """
        
        try:
            # Load swagger analysis
            swagger_analysis = self._load_swagger_analysis(swagger_analysis_file)
            
            # Generate test cases
            return await self.generate_test_cases_from_analysis(
                swagger_analysis, 
                endpoint_filter, 
                method_filter
            )
            
        except Exception as e:
            raise
    
    async def generate_test_cases_from_analysis(
        self,
        swagger_analysis: Dict[str, Any],
        endpoint_filter: Optional[str] = None,
        method_filter: Optional[str] = None
    ) -> List[TestGenerationResult]:
        """
        Generate test cases from swagger analysis dictionary.
        
        Args:
            swagger_analysis: Swagger analysis data (from JSON)
            endpoint_filter: Optional - filter by specific endpoint
            method_filter: Optional - filter by HTTP method
            
        Returns:
            List of TestGenerationResult, one per endpoint
        """
        
        results = []
        
        # Get analysis data
        analysis_data = swagger_analysis.get("analysis", swagger_analysis)
        endpoints = analysis_data.get("endpoints", [])
        
        if not endpoints:
            raise InvalidSwaggerAnalysisError("No endpoints found in swagger analysis")
        
        # Filter endpoints if specified
        filtered_endpoints = self._filter_endpoints(endpoints, endpoint_filter, method_filter)
        
        # Generate test cases for each endpoint
        for endpoint_data in filtered_endpoints:
            try:
                result = await self._generate_for_endpoint(endpoint_data)
                results.append(result)
            except Exception as e:
                # Log error but continue with other endpoints
                endpoint = endpoint_data.get("path", "unknown")
                method = endpoint_data.get("method", "unknown")
                logger.warning(
                    f"Failed to generate tests for {method} {endpoint}",
                    exc_info=True,
                    extra={"endpoint": endpoint, "method": method}
                )
                continue
        
        return results
    
    async def _generate_for_endpoint(self, endpoint_data: Dict[str, Any]) -> TestGenerationResult:
        """Generate test cases for a single endpoint."""
        endpoint = endpoint_data.get("path", "")
        http_method = endpoint_data.get("method", "")
        
        # Step 1: Identify partitions for all fields
        partition_sets = self._identify_all_partitions(endpoint_data)
        
        # Step 2: Build test cases
        test_cases = self.test_case_builder.build_test_cases_for_endpoint(
            endpoint=endpoint,
            http_method=http_method,
            partition_sets=partition_sets,
            endpoint_data=endpoint_data
        )
        
        # Step 3: Calculate metrics
        total_partitions = sum(len(ps.partitions) for ps in partition_sets)
        valid_partitions = sum(len(ps.get_valid_partitions()) for ps in partition_sets)
        invalid_partitions = sum(len(ps.get_invalid_partitions()) for ps in partition_sets)
        
        # Calculate coverage
        covered_partition_ids = set()
        for test_case in test_cases:
            for partition in test_case.partitions_covered:
                covered_partition_ids.add(partition.partition_id)
        
        coverage = (len(covered_partition_ids) / total_partitions * 100) if total_partitions > 0 else 0
        
        # Generate summary
        summary = self._generate_summary(
            endpoint, http_method, test_cases, partition_sets, coverage
        )
        
        return TestGenerationResult(
            endpoint=endpoint,
            http_method=http_method,
            technique=SwaggerConstants.TEST_TECHNIQUE_EP,
            total_partitions=total_partitions,
            valid_partitions=valid_partitions,
            invalid_partitions=invalid_partitions,
            partition_sets=partition_sets,
            test_cases=test_cases,
            coverage_percentage=coverage,
            summary=summary
        )
    
    def _identify_all_partitions(self, endpoint_data: Dict[str, Any]) -> List[PartitionSet]:
        """Identify partitions for all fields in the endpoint."""
        partition_sets = []
        endpoint = endpoint_data.get("path", "")
        
        # Process headers
        headers = endpoint_data.get("headers", [])
        for header in headers:
            if header.get("required"):  # Only process required headers for now
                partition_set = self.partition_identifier.identify_partitions_for_field(
                    field_name=header.get("name"),
                    field_data=header,
                    endpoint=endpoint
                )
                partition_sets.append(partition_set)
        
        # Process path parameters
        path_params = endpoint_data.get("path_parameters", [])
        for param in path_params:
            partition_set = self.partition_identifier.identify_partitions_for_field(
                field_name=param.get("name"),
                field_data=param,
                endpoint=endpoint
            )
            partition_sets.append(partition_set)
        
        # Process query parameters
        query_params = endpoint_data.get("query_parameters", [])
        for param in query_params:
            if param.get("required"):  # Only required query params
                partition_set = self.partition_identifier.identify_partitions_for_field(
                    field_name=param.get("name"),
                    field_data=param,
                    endpoint=endpoint
                )
                partition_sets.append(partition_set)
        
        # Process request body fields
        request_body = endpoint_data.get("request_body")
        if request_body and isinstance(request_body, dict):
            for field_name, field_data in request_body.items():
                if isinstance(field_data, dict):
                    partition_set = self.partition_identifier.identify_partitions_for_field(
                        field_name=field_name,
                        field_data=field_data,
                        endpoint=endpoint
                    )
                    partition_sets.append(partition_set)
        
        return partition_sets
    
    def _filter_endpoints(
        self,
        endpoints: List[Dict[str, Any]],
        endpoint_filter: Optional[str],
        method_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Filter endpoints by path and/or method."""
        filtered = endpoints
        
        if endpoint_filter:
            filtered = [e for e in filtered if e.get("path") == endpoint_filter]
        
        if method_filter:
            method_upper = method_filter.upper()
            filtered = [e for e in filtered if e.get("method", "").upper() == method_upper]
        
        return filtered
    
    def _generate_summary(
        self,
        endpoint: str,
        http_method: str,
        test_cases: List[TestCase],
        partition_sets: List[PartitionSet],
        coverage: float
    ) -> str:
        """Generate human-readable summary of test generation."""
        positive_tests = [tc for tc in test_cases if "positive" in tc.tags]
        negative_tests = [tc for tc in test_cases if "negative" in tc.tags]
        
        summary = f"""
Test Generation Summary for {http_method} {endpoint}
{'=' * 60}
Technique: Equivalence Partitioning (ISTQB v4)

Partition Analysis:
- Total Fields Analyzed: {len(partition_sets)}
- Total Partitions Identified: {sum(len(ps.partitions) for ps in partition_sets)}
- Valid Partitions: {sum(len(ps.get_valid_partitions()) for ps in partition_sets)}
- Invalid Partitions: {sum(len(ps.get_invalid_partitions()) for ps in partition_sets)}

Test Cases Generated: {len(test_cases)}
- Positive Tests: {len(positive_tests)}
- Negative Tests: {len(negative_tests)}

Coverage: {coverage:.1f}% (ISTQB requires 100%)

Test Case Breakdown:
"""
        
        for test_case in test_cases:
            summary += f"  • {test_case.test_name} [{test_case.priority.value}]\n"
        
        return summary.strip()
    
    def _load_swagger_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Load swagger analysis from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with swagger analysis data
            
        Raises:
            InvalidSwaggerAnalysisError: If file cannot be loaded or is invalid
        """
        try:
            path = Path(file_path)
            data = FileOperations.load_json(path)
            
            # Validate basic structure
            if "analysis" not in data and "endpoints" not in data:
                raise InvalidSwaggerAnalysisError(
                    "Invalid swagger analysis format: missing 'analysis' or 'endpoints'"
                )
            
            return data
            
        except json.JSONDecodeError as e:
            raise InvalidSwaggerAnalysisError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise InvalidSwaggerAnalysisError(f"Failed to load swagger analysis: {str(e)}")
