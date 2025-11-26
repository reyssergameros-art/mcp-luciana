"""Refactored test case builder using SOLID principles and dynamic resolution."""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..domain.models import (
    TestCase, EquivalencePartition, PartitionSet, PartitionType, 
    TestCasePriority, PartitionCategory
)
from ..domain.exceptions import TestCaseBuildError
from .status_code_resolver import StatusCodeResolver
from .error_code_resolver import ErrorCodeResolver
from src.shared.config import SwaggerConstants


class TestCaseBuilderRefactored:
    """
    Refactored test case builder following SOLID principles.
    
    Improvements:
    - Single Responsibility: Focuses on building test cases
    - Dependency Injection: Uses resolvers for status codes and error codes
    - No Hardcoding: All data comes from swagger analysis or resolvers
    - Open/Closed: Easy to extend with new test generation strategies
    
    Responsibilities:
    - Build complete test cases from partitions
    - Generate test case IDs
    - Determine test priorities
    - Create test data combining multiple partitions
    - Delegate status code and error code resolution
    """
    
    def __init__(
        self,
        status_resolver: StatusCodeResolver = None,
        error_resolver: ErrorCodeResolver = None
    ):
        """
        Initialize test case builder with resolvers.
        
        Args:
            status_resolver: Resolver for HTTP status codes
            error_resolver: Resolver for error codes
        """
        self.test_counter = 0
        self.status_resolver = status_resolver or StatusCodeResolver()
        self.error_resolver = error_resolver or ErrorCodeResolver()
    
    def build_test_cases_for_endpoint(
        self,
        endpoint: str,
        http_method: str,
        partition_sets: List[PartitionSet],
        endpoint_data: Dict[str, Any]
    ) -> List[TestCase]:
        """
        Build test cases for an endpoint using equivalence partitioning.
        
        Strategy:
        1. Generate positive test cases (all valid partitions)
        2. Generate negative test cases (one invalid partition at a time)
        
        Args:
            endpoint: API endpoint path
            http_method: HTTP method (GET, POST, etc.)
            partition_sets: All partition sets for this endpoint
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            List of TestCase objects
            
        Raises:
            TestCaseBuildError: If test case cannot be built
        """
        try:
            test_cases = []
            
            # Build positive test cases (all valid partitions)
            positive_tests = self._build_positive_test_cases(
                endpoint, http_method, partition_sets, endpoint_data
            )
            test_cases.extend(positive_tests)
            
            # Build negative test cases (one invalid partition per test)
            negative_tests = self._build_negative_test_cases(
                endpoint, http_method, partition_sets, endpoint_data
            )
            test_cases.extend(negative_tests)
            
            return test_cases
            
        except Exception as e:
            raise TestCaseBuildError(
                f"Cannot build test cases for {http_method} {endpoint}: {str(e)}"
            )
    
    def _build_positive_test_cases(
        self,
        endpoint: str,
        http_method: str,
        partition_sets: List[PartitionSet],
        endpoint_data: Dict[str, Any]
    ) -> List[TestCase]:
        """
        Build positive test cases using valid partitions from all sets.
        
        Following ISTQB: Each valid partition should be exercised at least once.
        """
        positive_tests = []
        
        # Get one valid partition from each set
        valid_partitions = []
        for partition_set in partition_sets:
            valid_from_set = partition_set.get_valid_partitions()
            if valid_from_set:
                valid_partitions.append(valid_from_set[0])
        
        if not valid_partitions:
            return positive_tests
        
        # Build test case with all valid values
        test_case_id = self._generate_test_case_id(endpoint, http_method, "valid_all")
        test_data = self._build_test_data_from_partitions(valid_partitions)
        
        # Resolve expected status code dynamically
        expected_status = self.status_resolver.get_success_status_code(
            http_method, endpoint_data
        )
        
        test_case = TestCase(
            test_case_id=test_case_id,
            test_name=f"{http_method} {endpoint} - All Valid Inputs",
            technique=SwaggerConstants.TEST_TECHNIQUE_EP,
            endpoint=endpoint,
            http_method=http_method,
            priority=TestCasePriority.HIGH,
            objective="Verify endpoint accepts all valid input values within equivalence partitions",
            partitions_covered=valid_partitions,
            test_data=test_data,
            expected_result=f"Request processed successfully with status {expected_status}",
            expected_status_code=expected_status,
            preconditions=self._generate_preconditions(endpoint_data),
            steps=self._generate_test_steps(
                http_method, endpoint, test_data, valid_partitions, endpoint_data
            ),
            tags=["positive", "equivalence_partition", "valid", http_method.lower()]
        )
        
        positive_tests.append(test_case)
        return positive_tests
    
    def _build_negative_test_cases(
        self,
        endpoint: str,
        http_method: str,
        partition_sets: List[PartitionSet],
        endpoint_data: Dict[str, Any]
    ) -> List[TestCase]:
        """
        Build negative test cases using invalid partitions.
        
        Following ISTQB: Each invalid partition should be tested separately
        to isolate failure conditions.
        """
        negative_tests = []
        
        # For each invalid partition, create a test case
        for partition_set in partition_sets:
            invalid_partitions = partition_set.get_invalid_partitions()
            
            for invalid_partition in invalid_partitions:
                # Create test with this invalid partition and valid values for others
                test_partitions = [invalid_partition]
                
                # Add valid partitions from other sets
                for other_set in partition_sets:
                    if other_set.field_name != partition_set.field_name:
                        valid_from_other = other_set.get_valid_partitions()
                        if valid_from_other:
                            test_partitions.append(valid_from_other[0])
                
                # Build test case
                test_case_id = self._generate_test_case_id(
                    endpoint, 
                    http_method, 
                    f"invalid_{partition_set.field_name}_{invalid_partition.category.value}"
                )
                
                test_data = self._build_test_data_from_partitions(test_partitions)
                
                # Resolve expected error dynamically from swagger ONLY
                expected_error_code = self._get_expected_error_code(
                    invalid_partition, partition_set.field_name, endpoint_data
                )
                
                # If no error code found in swagger, use generic description
                if expected_error_code:
                    expected_status = self.status_resolver.get_error_status_code(
                        expected_error_code, endpoint_data
                    )
                    expected_result_text = f"Request rejected with error {expected_error_code} and status {expected_status}"
                else:
                    # No error code in swagger - use generic validation error
                    expected_status = 400  # Generic Bad Request
                    expected_result_text = f"Request rejected with validation error and status {expected_status}"
                
                test_case = TestCase(
                    test_case_id=test_case_id,
                    test_name=f"{http_method} {endpoint} - Invalid {partition_set.field_name} ({invalid_partition.category.value})",
                    technique=SwaggerConstants.TEST_TECHNIQUE_EP,
                    endpoint=endpoint,
                    http_method=http_method,
                    priority=self._determine_priority(invalid_partition),
                    objective=f"Verify endpoint rejects invalid {partition_set.field_name}: {invalid_partition.description}",
                    partitions_covered=test_partitions,
                    test_data=test_data,
                    expected_result=expected_result_text,
                    expected_status_code=expected_status,
                    preconditions=self._generate_preconditions(endpoint_data),
                    steps=self._generate_test_steps(
                        http_method, endpoint, test_data, test_partitions, 
                        endpoint_data, is_negative=True
                    ),
                    tags=[
                        "negative", "equivalence_partition", "invalid", 
                        invalid_partition.category.value, http_method.lower()
                    ]
                )
                
                negative_tests.append(test_case)
        
        return negative_tests
    
    def _build_test_data_from_partitions(
        self, 
        partitions: List[EquivalencePartition]
    ) -> Dict[str, Any]:
        """
        Build test data dictionary from list of partitions.
        
        Combines test values from multiple partitions into a single test data payload.
        """
        test_data = {}
        
        for partition in partitions:
            field_name = partition.field_name
            
            # Handle special case: missing required field (use None or omit)
            if partition.category == PartitionCategory.REQUIRED and partition.test_value is None:
                # Omit field entirely (don't add to test_data)
                continue
            
            test_data[field_name] = partition.test_value
        
        return test_data
    
    def _get_expected_error_code(
        self,
        partition: EquivalencePartition,
        field_name: str,
        endpoint_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get expected error code dynamically from swagger metadata ONLY.
        
        Does NOT use hardcoded fallbacks. If swagger doesn't define error codes,
        returns None to indicate undefined behavior.
        
        Args:
            partition: Invalid partition
            field_name: Field name
            endpoint_data: Endpoint metadata
            
        Returns:
            Error code from swagger, or None if not defined
        """
        # ONLY use swagger metadata - no hardcoded fallbacks
        resolved_error = self.error_resolver.get_error_code_for_constraint(
            field_name,
            partition.category.value,
            partition.constraint_details,
            endpoint_data
        )
        
        # Return None if not found - caller must handle
        return resolved_error
    
    def _determine_priority(self, partition: EquivalencePartition) -> TestCasePriority:
        """Determine test case priority based on partition characteristics."""
        # Required fields and format validations are high priority
        if partition.category in [PartitionCategory.REQUIRED, PartitionCategory.FORMAT]:
            return TestCasePriority.HIGH
        
        # Length and range validations are medium priority
        if partition.category in [PartitionCategory.LENGTH, PartitionCategory.RANGE]:
            return TestCasePriority.MEDIUM
        
        # Type and enum validations are lower priority
        return TestCasePriority.LOW
    
    def _generate_preconditions(self, endpoint_data: Dict[str, Any]) -> List[str]:
        """
        Generate preconditions dynamically from endpoint metadata.
        
        Args:
            endpoint_data: Endpoint metadata from swagger
            
        Returns:
            List of precondition strings
        """
        preconditions = [
            "API server is running and accessible",
            "Test environment is properly configured"
        ]
        
        # Add authentication if required headers present
        headers = endpoint_data.get("headers", [])
        if headers:
            header_names = [h.get("name", "") for h in headers if h.get("required", False)]
            if header_names:
                header_list = ", ".join(header_names)
                preconditions.append(f"Required headers ({header_list}) are available")
        
        return preconditions
    
    def _generate_test_steps(
        self,
        http_method: str,
        endpoint: str,
        test_data: Dict[str, Any],
        partitions: List[EquivalencePartition],
        endpoint_data: Dict[str, Any],
        is_negative: bool = False
    ) -> List[str]:
        """Generate detailed test execution steps dynamically."""
        steps = []
        
        # Step 1: Prepare test data
        data_description = ", ".join([f"{k}={v}" for k, v in test_data.items()])
        steps.append(f"Prepare test data: {data_description}")
        
        # Step 2: Set headers (dynamically from swagger)
        headers = endpoint_data.get("headers", [])
        if headers:
            required_headers = [h.get("name") for h in headers if h.get("required", False)]
            if required_headers:
                header_list = ", ".join(required_headers)
                steps.append(f"Set required headers ({header_list}) with valid UUIDs")
        
        # Step 3: Send request
        if http_method.upper() in ["POST", "PUT", "PATCH"]:
            steps.append(f"Send {http_method} request to {endpoint} with test data in request body")
        else:
            steps.append(f"Send {http_method} request to {endpoint}")
        
        # Step 4: Verify response
        if is_negative:
            invalid_partition = next(
                (p for p in partitions if p.partition_type == PartitionType.INVALID), 
                None
            )
            if invalid_partition:
                expected_error = self._get_expected_error_code(
                    invalid_partition, 
                    invalid_partition.field_name, 
                    endpoint_data
                )
                if expected_error:
                    steps.append(f"Verify response contains error code {expected_error}")
                else:
                    steps.append("Verify response contains validation error code")
                steps.append("Verify response status indicates validation failure")
        else:
            steps.append("Verify response status indicates success")
            steps.append("Verify response body structure matches specification")
        
        # Step 5: Log result
        steps.append("Log test result with timestamp and execution details")
        
        return steps
    
    def _generate_test_case_id(self, endpoint: str, http_method: str, scenario: str) -> str:
        """Generate unique test case ID."""
        self.test_counter += 1
        endpoint_safe = endpoint.replace("/", "").replace("{", "").replace("}", "").strip()
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{SwaggerConstants.TEST_ID_PREFIX_EP}{http_method.upper()}{endpoint_safe}{scenario}{timestamp}_{self.test_counter}"
