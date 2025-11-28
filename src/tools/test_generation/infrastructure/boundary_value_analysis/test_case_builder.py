"""
Test case builder for Boundary Value Analysis.
Generates test cases exercising boundary values and their neighbors.
"""
from typing import List, Dict, Any
from datetime import datetime
from ...domain.boundary_value_analysis.models import (
    BVATestCase, BoundaryValue, BVAVersion, BoundaryType
)


class BVATestCaseBuilder:
    """Builds BVA test cases from identified boundaries."""
    
    @staticmethod
    def build_test_cases(
        endpoint: str,
        http_method: str,
        boundaries: List[BoundaryValue],
        all_fields: Dict[str, Any],
        bva_version: BVAVersion
    ) -> List[BVATestCase]:
        """
        Build test cases exercising boundary values according to ISTQB v4.
        
        Args:
            endpoint: API endpoint path
            http_method: HTTP method
            boundaries: List of identified boundaries
            all_fields: All field definitions with their valid values
            bva_version: BVA version (2-value or 3-value)
            
        Returns:
            List of BVATestCase objects
        """
        test_cases = []
        test_counter = 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for boundary in boundaries:
            # Get test values based on BVA version
            if bva_version == BVAVersion.TWO_VALUE:
                test_values = boundary.get_test_values_2value()
            else:
                test_values = boundary.get_test_values_3value()
            
            for value in test_values:
                # Build test data with all fields
                test_data = BVATestCaseBuilder._build_test_data(
                    boundary.field_name,
                    value,
                    all_fields
                )
                
                # Determine expected status
                is_valid = BVATestCaseBuilder._is_valid_value(value, boundary)
                expected_status = 200 if http_method == "GET" else (201 if is_valid else 400)
                
                # Build test case ID
                value_type = BVATestCaseBuilder._get_value_type(value, boundary)
                test_id = f"BVA{http_method}{endpoint.replace('/', '').replace('{', '').replace('}', '')}{boundary.field_name}{value_type}{timestamp}_{test_counter}"
                
                # Build test name
                test_name = f"{http_method} {endpoint} - {boundary.field_name} = {value_type}"
                
                test_case = BVATestCase(
                    test_case_id=test_id,
                    test_name=test_name,
                    endpoint=endpoint,
                    http_method=http_method,
                    test_data=test_data,
                    expected_status_code=expected_status,
                    expected_error=None if is_valid else "Validation error",
                    boundary_info={
                        "field": boundary.field_name,
                        "boundary_type": boundary.boundary_type.value,
                        "boundary_value": boundary.boundary_value,
                        "test_value": value,
                        "constraint_type": boundary.constraint_type
                    },
                    bva_version=bva_version.value,
                    priority="high" if not is_valid else "medium"
                )
                
                test_cases.append(test_case)
                test_counter += 1
        
        return test_cases
    
    @staticmethod
    def _build_test_data(
        boundary_field: str,
        boundary_value: Any,
        all_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build complete test data with boundary value for one field."""
        test_data = {}
        
        for field_name, field_info in all_fields.items():
            if field_name == boundary_field:
                test_data[field_name] = boundary_value
            else:
                # Use valid value for other fields
                test_data[field_name] = field_info.get("valid_value", "valid")
        
        return test_data
    
    @staticmethod
    def _is_valid_value(value: Any, boundary: BoundaryValue) -> bool:
        """Determine if the test value is valid or invalid."""
        if boundary.boundary_type == BoundaryType.MINIMUM:
            # Boundary value is valid, lower neighbor is invalid
            if value == boundary.lower_neighbor:
                return False
            return True
        else:  # MAXIMUM
            # Boundary value is valid, upper neighbor is invalid
            if value == boundary.upper_neighbor:
                return False
            return True
    
    @staticmethod
    def _get_value_type(value: Any, boundary: BoundaryValue) -> str:
        """Get descriptive type of the test value."""
        if value == boundary.boundary_value:
            return f"boundary{boundary.boundary_type.value.capitalize()}"
        elif value == boundary.lower_neighbor:
            return "belowMin" if boundary.boundary_type == BoundaryType.MINIMUM else "belowMax"
        elif value == boundary.upper_neighbor:
            return "aboveMin" if boundary.boundary_type == BoundaryType.MINIMUM else "aboveMax"
        return "unknown"
