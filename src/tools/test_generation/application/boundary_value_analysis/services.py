"""
Service for generating BVA test cases from Swagger analysis.
Follows ISTQB v4 definition of Boundary Value Analysis.
"""
import json
from typing import List, Dict, Any
from pathlib import Path
from ...domain.boundary_value_analysis.models import BVAResult, BVAVersion
from ...domain.boundary_value_analysis.exceptions import BVAError
from ...infrastructure.boundary_value_analysis.boundary_identifier import BoundaryIdentifier
from ...infrastructure.boundary_value_analysis.test_case_builder import BVATestCaseBuilder


class BVAService:
    """Service for BVA test case generation."""
    
    async def generate_bva_tests(
        self,
        swagger_analysis_file: str,
        bva_version: str = "2-value",
        endpoint_filter: str = None,
        method_filter: str = None
    ) -> List[BVAResult]:
        """
        Generate BVA test cases from swagger analysis.
        
        Args:
            swagger_analysis_file: Path to swagger analysis JSON
            bva_version: "2-value" or "3-value" BVA
            endpoint_filter: Optional endpoint filter
            method_filter: Optional HTTP method filter
            
        Returns:
            List of BVAResult objects
        """
        try:
            # Load swagger analysis
            with open(swagger_analysis_file, 'r', encoding='utf-8') as f:
                swagger_data = json.load(f)
            
            # Convert string to enum
            bva_version_enum = BVAVersion.TWO_VALUE if bva_version == "2-value" else BVAVersion.THREE_VALUE
            
            results = []
            endpoints = swagger_data.get("analysis", {}).get("endpoints", [])
            
            for endpoint_data in endpoints:
                # Apply filters
                if endpoint_filter and endpoint_data.get("path") != endpoint_filter:
                    continue
                if method_filter and endpoint_data.get("method") != method_filter:
                    continue
                
                result = self._generate_for_endpoint(
                    endpoint_data,
                    bva_version_enum
                )
                
                if result.boundaries_identified > 0:
                    results.append(result)
            
            return results
            
        except Exception as e:
            raise BVAError(f"Error generating BVA tests: {str(e)}")
    
    def _generate_for_endpoint(
        self,
        endpoint_data: Dict[str, Any],
        bva_version: BVAVersion
    ) -> BVAResult:
        """Generate BVA tests for a single endpoint."""
        endpoint = endpoint_data.get("path", "")
        http_method = endpoint_data.get("method", "")
        
        # Collect all fields with constraints
        all_fields = {}
        boundaries_list = []
        
        # Process headers
        for header in endpoint_data.get("headers", []):
            field_name = header.get("name", "")
            field_type = header.get("data_type", "")
            constraints = self._extract_constraints(header)
            
            # Store valid value for this field
            all_fields[field_name] = {
                "type": field_type,
                "valid_value": self._get_valid_value(field_type, constraints)
            }
            
            # Identify boundaries
            field_boundaries = BoundaryIdentifier.identify_boundaries(
                field_name, field_type, constraints, bva_version
            )
            boundaries_list.extend(field_boundaries)
        
        # Process path parameters
        for param in endpoint_data.get("path_parameters", []):
            field_name = param.get("name", "")
            field_type = param.get("data_type", "")
            constraints = self._extract_constraints(param)
            
            all_fields[field_name] = {
                "type": field_type,
                "valid_value": self._get_valid_value(field_type, constraints)
            }
            
            field_boundaries = BoundaryIdentifier.identify_boundaries(
                field_name, field_type, constraints, bva_version
            )
            boundaries_list.extend(field_boundaries)
        
        # Process query parameters
        for param in endpoint_data.get("query_parameters", []):
            field_name = param.get("name", "")
            field_type = param.get("data_type", "")
            constraints = self._extract_constraints(param)
            
            all_fields[field_name] = {
                "type": field_type,
                "valid_value": self._get_valid_value(field_type, constraints)
            }
            
            field_boundaries = BoundaryIdentifier.identify_boundaries(
                field_name, field_type, constraints, bva_version
            )
            boundaries_list.extend(field_boundaries)
        
        # Process request body fields
        request_body = endpoint_data.get("request_body")
        if request_body and isinstance(request_body, dict):
            for field_name, field_info in request_body.items():
                if isinstance(field_info, dict):
                    field_type = field_info.get("data_type", "")
                    constraints = self._extract_constraints(field_info)
                    
                    all_fields[field_name] = {
                        "type": field_type,
                        "valid_value": self._get_valid_value(field_type, constraints)
                    }
                    
                    field_boundaries = BoundaryIdentifier.identify_boundaries(
                        field_name, field_type, constraints, bva_version
                    )
                    boundaries_list.extend(field_boundaries)
        
        # Generate test cases
        test_cases = BVATestCaseBuilder.build_test_cases(
            endpoint=endpoint,
            http_method=http_method,
            boundaries=boundaries_list,
            all_fields=all_fields,
            bva_version=bva_version
        )
        
        # Calculate coverage
        # For 2-value: 2 coverage items per boundary (boundary + 1 neighbor)
        # For 3-value: 3 coverage items per boundary (boundary + 2 neighbors)
        items_per_boundary = 2 if bva_version == BVAVersion.TWO_VALUE else 3
        total_coverage_items = len(boundaries_list) * items_per_boundary
        tested_items = len(test_cases)
        
        result = BVAResult(
            endpoint=endpoint,
            http_method=http_method,
            bva_version=bva_version.value,
            boundaries_identified=len(boundaries_list),
            test_cases=test_cases,
            coverage_items_tested=tested_items,
            coverage_items_total=total_coverage_items,
            metadata={
                "technique": f"Boundary Value Analysis ({bva_version.value})",
                "total_fields_analyzed": len(all_fields)
            }
        )
        
        result.calculate_coverage()
        return result
    
    def _extract_constraints(self, field_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract constraints from field info."""
        return {
            "min_length": field_info.get("min_length"),
            "max_length": field_info.get("max_length"),
            "minimum": field_info.get("minimum"),
            "maximum": field_info.get("maximum"),
            "min_items": field_info.get("min_items"),
            "max_items": field_info.get("max_items"),
        }
    
    def _get_valid_value(self, field_type: str, constraints: Dict[str, Any]) -> Any:
        """Get a valid value for a field based on its type and constraints."""
        if field_type == "string":
            min_len = constraints.get("min_length", 3)
            max_len = constraints.get("max_length", 50)
            length = min(min_len + 5, max_len) if min_len else 10
            return "a" * length
        elif field_type in ["integer", "int", "int32", "int64"]:
            minimum = constraints.get("minimum", 1)
            maximum = constraints.get("maximum", 100)
            return (minimum + maximum) // 2 if minimum and maximum else minimum or 50
        elif field_type in ["number", "float"]:
            minimum = constraints.get("minimum", 1.0)
            maximum = constraints.get("maximum", 100.0)
            return (minimum + maximum) / 2 if minimum and maximum else minimum or 50.0
        elif field_type == "array":
            min_items = constraints.get("min_items", 1)
            return ["item"] * (min_items + 1)
        elif field_type == "boolean":
            return True
        else:
            return "valid_value"
