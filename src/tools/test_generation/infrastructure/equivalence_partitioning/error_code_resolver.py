"""Resolves expected error codes from swagger analysis dynamically."""
from typing import Dict, Any, Optional, List


class ErrorCodeResolver:
    """
    Resolves expected error codes from swagger endpoint metadata.
    
    Follows Single Responsibility Principle - only handles error code resolution.
    Eliminates hardcoded error codes by extracting them from swagger analysis.
    """
    
    def __init__(self):
        """Initialize error code resolver."""
        pass
    
    def get_error_code_for_constraint(
        self,
        field_name: str,
        constraint_category: str,
        constraint_details: Dict[str, Any],
        endpoint_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get expected error code for constraint violation.
        
        Searches swagger error_codes to find matching error for constraint type.
        
        Args:
            field_name: Name of the field being validated
            constraint_category: Category like "required", "length", "format"
            constraint_details: Details about the constraint
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            Error code string (e.g., "RBV-001") or None
        """
        # Search error responses for matching error code
        responses = endpoint_data.get("responses", [])
        
        for response in responses:
            # Only check error responses (4xx, 5xx)
            status_code = str(response.get("status_code", ""))
            if not status_code.startswith(("4", "5")):
                continue
            
            error_codes = response.get("error_codes", [])
            validation_errors = response.get("validation_errors", [])
            
            # Search through error codes
            for error_info in error_codes + validation_errors:
                if self._matches_constraint(
                    error_info,
                    field_name,
                    constraint_category,
                    constraint_details
                ):
                    return error_info.get("code")
        
        # Fallback: Infer from constraint category
        return self._infer_error_code_from_category(
            constraint_category,
            constraint_details
        )
    
    def _matches_constraint(
        self,
        error_info: Dict[str, Any],
        field_name: str,
        constraint_category: str,
        constraint_details: Dict[str, Any]
    ) -> bool:
        """
        Check if error info matches the constraint violation.
        
        Args:
            error_info: Error information from swagger
            field_name: Field name
            constraint_category: Constraint category
            constraint_details: Constraint details
            
        Returns:
            True if error matches constraint
        """
        error_type = error_info.get("type", "").lower()
        error_desc = error_info.get("description", "").lower()
        
        # Category mapping to error types and keywords
        category_patterns = {
            "required": {
                "types": ["required_field", "missing_field"],
                "keywords": ["required", "missing", "must provide", "mandatory"]
            },
            "length": {
                "types": ["length_error", "min_length", "max_length"],
                "keywords": ["length", "characters", "char", "too short", "too long"]
            },
            "format": {
                "types": ["format_error", "pattern_error", "invalid_format"],
                "keywords": ["format", "pattern", "invalid", "malformed", "correctly formatted"]
            },
            "range": {
                "types": ["range_error", "min_value", "max_value"],
                "keywords": ["range", "minimum", "maximum", "between", "exceeds"]
            },
            "type": {
                "types": ["type_error", "invalid_type"],
                "keywords": ["type", "invalid", "expected", "wrong type"]
            },
            "enum": {
                "types": ["enum_error", "invalid_value"],
                "keywords": ["enum", "allowed", "valid values", "not allowed"]
            }
        }
        
        pattern = category_patterns.get(constraint_category.lower(), {})
        types = pattern.get("types", [])
        keywords = pattern.get("keywords", [])
        
        # Check if error type matches
        if error_type in types:
            return True
        
        # Check if keywords match in description
        if any(keyword in error_desc for keyword in keywords):
            # Additional validation: check field name if mentioned
            if field_name.lower() in error_desc or field_name.replace("-", "").replace("_", "").lower() in error_desc.replace("-", "").replace("_", ""):
                return True
            # If field not mentioned, still match on category
            return True
        
        return False
    
    def _infer_error_code_from_category(
        self,
        constraint_category: str,
        constraint_details: Dict[str, Any]
    ) -> Optional[str]:
        """
        Attempt to infer error code pattern from constraint category.
        
        This is a LAST RESORT fallback when error code is not found in swagger.
        Returns None to allow caller to decide on fallback behavior.
        
        Args:
            constraint_category: Constraint category
            constraint_details: Constraint details
            
        Returns:
            None - indicates no error code found, caller must handle
        """
        # NO hardcoded error codes
        # If swagger doesn't define error codes, we cannot infer them
        # Each API has different error code conventions
        return None
    
    def get_all_error_codes(self, endpoint_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all error codes defined for an endpoint.
        
        Args:
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            List of all error code dictionaries
        """
        all_errors = []
        
        responses = endpoint_data.get("responses", [])
        for response in responses:
            status_code = str(response.get("status_code", ""))
            
            # Only include error responses
            if not status_code.startswith(("4", "5")):
                continue
            
            error_codes = response.get("error_codes", [])
            validation_errors = response.get("validation_errors", [])
            
            for error_info in error_codes + validation_errors:
                all_errors.append({
                    "code": error_info.get("code", ""),
                    "type": error_info.get("type", ""),
                    "description": error_info.get("description", ""),
                    "http_status": error_info.get("http_status", status_code),
                    "sub_codes": error_info.get("sub_codes", [])
                })
        
        return all_errors
