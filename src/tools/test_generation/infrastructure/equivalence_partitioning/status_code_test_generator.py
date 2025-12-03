"""
Generates test cases for all HTTP status codes found in swagger analysis.

Ensures coverage of ALL response codes (2xx, 4xx, 5xx) identified in the API specification,
not just generic success/error cases.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...domain.equivalence_partitioning.models import (
    TestCase, TestCasePriority, EquivalencePartition, PartitionType
)
from src.shared.config import SwaggerConstants


class StatusCodeTestGenerator:
    """
    Generates comprehensive test cases for all HTTP status codes.
    
    Follows ISTQB principle: Test all defined response codes, not just happy path.
    
    Responsibilities:
    - Extract all unique status codes from swagger responses
    - Generate at least one test case per status code
    - Create appropriate test data based on status code semantics
    - Handle success codes (2xx), client errors (4xx), server errors (5xx)
    """
    
    def __init__(self):
        """Initialize status code test generator."""
        self.test_counter = 0
    
    def generate_status_code_tests(
        self,
        endpoint: str,
        http_method: str,
        endpoint_data: Dict[str, Any]
    ) -> List[TestCase]:
        """
        Generate test cases for all status codes defined in swagger responses.
        
        Args:
            endpoint: API endpoint path
            http_method: HTTP method (GET, POST, etc.)
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            List of TestCase objects, one per unique status code
        """
        test_cases = []
        
        # Extract all unique status codes
        status_codes = self._extract_unique_status_codes(endpoint_data)
        
        for status_code in sorted(status_codes):
            # Find response info for this status code
            response_info = self._find_response_by_status(endpoint_data, status_code)
            
            if not response_info:
                continue
            
            # Generate test case based on status code category
            test_case = self._generate_test_case_for_status(
                endpoint, http_method, status_code, response_info, endpoint_data
            )
            
            if test_case:
                test_cases.append(test_case)
        
        return test_cases
    
    def _extract_unique_status_codes(self, endpoint_data: Dict[str, Any]) -> List[int]:
        """Extract all unique status codes from endpoint responses."""
        status_codes = set()
        
        responses = endpoint_data.get("responses", [])
        for response in responses:
            status_code_str = str(response.get("status_code", ""))
            try:
                status_code = int(status_code_str)
                status_codes.add(status_code)
            except ValueError:
                # Skip non-numeric status codes (e.g., "default")
                continue
        
        return list(status_codes)
    
    def _find_response_by_status(
        self, 
        endpoint_data: Dict[str, Any], 
        status_code: int
    ) -> Optional[Dict[str, Any]]:
        """Find response information for a specific status code."""
        responses = endpoint_data.get("responses", [])
        for response in responses:
            if int(response.get("status_code", 0)) == status_code:
                return response
        return None
    
    def _generate_test_case_for_status(
        self,
        endpoint: str,
        http_method: str,
        status_code: int,
        response_info: Dict[str, Any],
        endpoint_data: Dict[str, Any]
    ) -> Optional[TestCase]:
        """Generate a test case for a specific status code."""
        
        # Determine test case category
        if 200 <= status_code < 300:
            return self._generate_success_test(
                endpoint, http_method, status_code, response_info, endpoint_data
            )
        elif 400 <= status_code < 500:
            return self._generate_client_error_test(
                endpoint, http_method, status_code, response_info, endpoint_data
            )
        elif 500 <= status_code < 600:
            return self._generate_server_error_test(
                endpoint, http_method, status_code, response_info, endpoint_data
            )
        
        return None
    
    def _generate_success_test(
        self,
        endpoint: str,
        http_method: str,
        status_code: int,
        response_info: Dict[str, Any],
        endpoint_data: Dict[str, Any]
    ) -> TestCase:
        """Generate test case for success status codes (2xx)."""
        
        test_case_id = self._generate_test_case_id(
            endpoint, http_method, f"success_{status_code}"
        )
        
        # Create valid test data
        test_data = self._create_valid_test_data(endpoint_data)
        
        # Get status description
        status_descriptions = {
            200: "OK - Request succeeded",
            201: "Created - Resource created successfully",
            204: "No Content - Request succeeded with no response body",
            202: "Accepted - Request accepted for processing",
            203: "Non-Authoritative Information",
            205: "Reset Content",
            206: "Partial Content"
        }
        
        status_desc = status_descriptions.get(
            status_code, 
            f"Success ({status_code})"
        )
        
        description = response_info.get("description", status_desc)
        
        return TestCase(
            test_case_id=test_case_id,
            test_name=f"{http_method} {endpoint} - {status_desc}",
            technique=SwaggerConstants.TEST_TECHNIQUE_STATUS_CODE,
            endpoint=endpoint,
            http_method=http_method,
            priority=TestCasePriority.HIGH,
            objective=f"Verify endpoint returns {status_code} when: {description}",
            partitions_covered=[],
            test_data=test_data,
            expected_result=f"Request processed with status {status_code}",
            expected_status_code=status_code,
            preconditions=self._generate_preconditions(endpoint_data),
            steps=self._generate_test_steps(
                http_method, endpoint, test_data, status_code, "success"
            ),
            tags=["positive", "status_code_coverage", f"status_{status_code}", http_method.lower()]
        )
    
    def _generate_client_error_test(
        self,
        endpoint: str,
        http_method: str,
        status_code: int,
        response_info: Dict[str, Any],
        endpoint_data: Dict[str, Any]
    ) -> TestCase:
        """Generate test case for client error status codes (4xx)."""
        
        test_case_id = self._generate_test_case_id(
            endpoint, http_method, f"error_{status_code}"
        )
        
        # Create invalid test data based on status code
        test_data = self._create_error_test_data(
            status_code, response_info, endpoint_data
        )
        
        # Get status description
        status_descriptions = {
            400: "Bad Request - Invalid request data",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource does not exist",
            405: "Method Not Allowed",
            409: "Conflict - Resource already exists or state conflict",
            422: "Unprocessable Entity - Validation failed",
            429: "Too Many Requests - Rate limit exceeded"
        }
        
        status_desc = status_descriptions.get(
            status_code,
            f"Client Error ({status_code})"
        )
        
        description = response_info.get("description", status_desc)
        
        # Extract error codes if available
        error_codes = response_info.get("error_codes", [])
        expected_error = error_codes[0].get("code") if error_codes else None
        
        return TestCase(
            test_case_id=test_case_id,
            test_name=f"{http_method} {endpoint} - {status_desc}",
            technique=SwaggerConstants.TEST_TECHNIQUE_STATUS_CODE,
            endpoint=endpoint,
            http_method=http_method,
            priority=TestCasePriority.HIGH,
            objective=f"Verify endpoint returns {status_code} when: {description}",
            partitions_covered=[],
            test_data=test_data,
            expected_result=f"Request rejected with status {status_code}",
            expected_status_code=status_code,
            expected_error=expected_error,
            preconditions=self._generate_preconditions(endpoint_data),
            steps=self._generate_test_steps(
                http_method, endpoint, test_data, status_code, "error"
            ),
            tags=["negative", "status_code_coverage", f"status_{status_code}", http_method.lower()]
        )
    
    def _generate_server_error_test(
        self,
        endpoint: str,
        http_method: str,
        status_code: int,
        response_info: Dict[str, Any],
        endpoint_data: Dict[str, Any]
    ) -> TestCase:
        """Generate test case for server error status codes (5xx)."""
        
        test_case_id = self._generate_test_case_id(
            endpoint, http_method, f"server_error_{status_code}"
        )
        
        status_descriptions = {
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        
        status_desc = status_descriptions.get(
            status_code,
            f"Server Error ({status_code})"
        )
        
        description = response_info.get("description", status_desc)
        
        return TestCase(
            test_case_id=test_case_id,
            test_name=f"{http_method} {endpoint} - {status_desc}",
            technique=SwaggerConstants.TEST_TECHNIQUE_STATUS_CODE,
            endpoint=endpoint,
            http_method=http_method,
            priority=TestCasePriority.MEDIUM,
            objective=f"Verify endpoint handles server error {status_code}: {description}",
            partitions_covered=[],
            test_data={},
            expected_result=f"Server error response with status {status_code}",
            expected_status_code=status_code,
            preconditions=["Server is in error state or specific conditions trigger this error"],
            steps=[
                f"Trigger conditions that cause {status_code} error",
                f"Send {http_method} request to {endpoint}",
                f"Verify response status is {status_code}",
                "Verify error response structure"
            ],
            tags=["negative", "status_code_coverage", f"status_{status_code}", "server_error", http_method.lower()]
        )
    
    def _create_valid_test_data(self, endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create valid test data for success test cases."""
        test_data = {}
        
        # Add valid headers
        headers = endpoint_data.get("headers", [])
        for header in headers:
            if header.get("required"):
                name = header.get("name")
                example = header.get("example")
                if example:
                    test_data[name] = example
                elif header.get("format") == "uuid":
                    test_data[name] = "550e8400-e29b-41d4-a716-446655440000"
        
        # Add valid path parameters
        path_params = endpoint_data.get("path_parameters", [])
        for param in path_params:
            name = param.get("name")
            example = param.get("example")
            if example:
                test_data[name] = example
            elif param.get("data_type") == "integer":
                test_data[name] = 1
        
        # Add valid query parameters
        query_params = endpoint_data.get("query_parameters", [])
        for param in query_params:
            if param.get("required"):
                name = param.get("name")
                example = param.get("example")
                if example:
                    test_data[name] = example
        
        # Add valid request body
        request_body = endpoint_data.get("request_body")
        if request_body:
            body_fields = request_body.get("fields", [])
            body_data = {}
            for field in body_fields:
                if field.get("required"):
                    name = field.get("name")
                    example = field.get("example")
                    if example:
                        body_data[name] = example
            if body_data:
                test_data["body"] = body_data
        
        return test_data
    
    def _create_error_test_data(
        self, 
        status_code: int, 
        response_info: Dict[str, Any],
        endpoint_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create test data that triggers specific error status code."""
        
        # Start with valid data
        test_data = self._create_valid_test_data(endpoint_data)
        
        # Modify data based on status code
        if status_code == 404:
            # Not Found - use non-existent ID
            path_params = endpoint_data.get("path_parameters", [])
            for param in path_params:
                if param.get("name") in ["id", "identifier"]:
                    test_data[param.get("name")] = 999999
        
        elif status_code == 409:
            # Conflict - use duplicate data (keep valid data, server will detect conflict)
            pass
        
        elif status_code == 422:
            # Unprocessable Entity - invalid business logic
            # Keep structure valid but values cause business rule violation
            pass
        
        return test_data
    
    def _generate_preconditions(self, endpoint_data: Dict[str, Any]) -> List[str]:
        """Generate preconditions for test case."""
        preconditions = ["API server is running and accessible"]
        
        # Add authentication if required
        headers = endpoint_data.get("headers", [])
        auth_headers = [h.get("name") for h in headers if "auth" in h.get("name", "").lower()]
        if auth_headers:
            preconditions.append("Valid authentication credentials are available")
        
        return preconditions
    
    def _generate_test_steps(
        self,
        http_method: str,
        endpoint: str,
        test_data: Dict[str, Any],
        status_code: int,
        test_type: str
    ) -> List[str]:
        """Generate test steps."""
        steps = []
        
        # Data preparation
        if test_data:
            data_summary = ", ".join([f"{k}={v}" for k, v in list(test_data.items())[:3]])
            steps.append(f"Prepare test data: {data_summary}")
        
        # Request execution
        steps.append(f"Send {http_method} request to {endpoint}")
        
        # Verification
        steps.append(f"Verify response status is {status_code}")
        
        if test_type == "success":
            steps.append("Verify response body structure matches specification")
        else:
            steps.append("Verify error response structure and error codes")
        
        return steps
    
    def _generate_test_case_id(self, endpoint: str, http_method: str, suffix: str) -> str:
        """Generate unique test case ID."""
        timestamp = datetime.now().strftime("%Y%m%d")
        self.test_counter += 1
        
        # Clean endpoint for ID
        clean_endpoint = endpoint.replace("/", "_").replace("{", "").replace("}", "").strip("_")
        
        return f"SC_{http_method}_{clean_endpoint}_{suffix}_{timestamp}_{self.test_counter}"
