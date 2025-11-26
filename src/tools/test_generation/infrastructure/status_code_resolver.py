"""Resolves HTTP status codes from swagger analysis dynamically."""
from typing import Dict, Any, List, Optional


class StatusCodeResolver:
    """
    Resolves expected HTTP status codes from swagger endpoint analysis.
    
    Follows Single Responsibility Principle - only handles status code resolution.
    Eliminates hardcoded status codes by extracting them from swagger metadata.
    """
    
    def __init__(self):
        """Initialize status code resolver."""
        pass
    
    def get_success_status_code(
        self,
        http_method: str,
        endpoint_data: Dict[str, Any]
    ) -> int:
        """
        Get expected success status code from swagger responses.
        
        Searches for 2xx status codes in endpoint responses.
        Falls back to standard REST conventions only if not found in swagger.
        
        Args:
            http_method: HTTP method (GET, POST, etc.)
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            Expected success HTTP status code
        """
        # First priority: Extract from swagger responses
        responses = endpoint_data.get("responses", [])
        for response in responses:
            status_code_str = str(response.get("status_code", ""))
            if status_code_str.startswith("2"):  # 2xx success codes
                return int(status_code_str)
        
        # Fallback: REST conventions
        method_upper = http_method.upper()
        fallback_codes = {
            "POST": 201,    # Created
            "DELETE": 204,  # No Content
            "PUT": 200,     # OK
            "PATCH": 200,   # OK
            "GET": 200,     # OK
        }
        
        return fallback_codes.get(method_upper, 200)
    
    def get_error_status_code(
        self,
        error_code: str,
        endpoint_data: Dict[str, Any]
    ) -> int:
        """
        Get expected error status code from swagger error definitions.
        
        Extracts status code from swagger error_codes metadata.
        
        Args:
            error_code: Error code (e.g., "RBV-001", "HDR-004")
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            Expected error HTTP status code
        """
        # Search in all responses for matching error code
        responses = endpoint_data.get("responses", [])
        for response in responses:
            error_codes = response.get("error_codes", [])
            for error_info in error_codes:
                if error_info.get("code") == error_code:
                    http_status = error_info.get("http_status", "400")
                    return int(http_status)
        
        # Fallback: Parse error code prefix
        return self._infer_status_from_error_prefix(error_code)
    
    def _infer_status_from_error_prefix(self, error_code: str) -> int:
        """
        Attempt to infer HTTP status code from error code pattern.
        
        This is a LAST RESORT fallback. Each API may have different conventions.
        Returns generic 400 Bad Request as safest default.
        
        Args:
            error_code: Error code string
            
        Returns:
            Generic 400 status code (cannot reliably infer without swagger data)
        """
        # Cannot reliably infer status codes without swagger metadata
        # Different APIs use different error code conventions
        # Example: One API might use "HDR-*" for 400, another for 401
        return 400  # Generic Bad Request - safest default
    
    def get_all_error_codes_for_field(
        self,
        field_name: str,
        constraint_category: str,
        endpoint_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get all relevant error codes for a field constraint violation.
        
        Args:
            field_name: Name of the field
            constraint_category: Category like "required", "length", "format"
            endpoint_data: Endpoint metadata from swagger analysis
            
        Returns:
            List of error code dictionaries with code, status, description
        """
        relevant_errors = []
        
        responses = endpoint_data.get("responses", [])
        for response in responses:
            # Only look at error responses (4xx, 5xx)
            status_code = str(response.get("status_code", ""))
            if not status_code.startswith(("4", "5")):
                continue
            
            error_codes = response.get("error_codes", [])
            validation_errors = response.get("validation_errors", [])
            
            # Match by field name and constraint type
            for error_info in error_codes + validation_errors:
                error_desc = error_info.get("description", "").lower()
                
                # Match constraint category to error description
                if self._matches_constraint_category(
                    constraint_category, 
                    error_desc, 
                    field_name
                ):
                    relevant_errors.append({
                        "code": error_info.get("code", ""),
                        "http_status": error_info.get("http_status", status_code),
                        "description": error_info.get("description", ""),
                        "type": error_info.get("type", "")
                    })
        
        return relevant_errors
    
    def _matches_constraint_category(
        self,
        category: str,
        error_description: str,
        field_name: str
    ) -> bool:
        """
        Check if error description matches constraint category.
        
        Args:
            category: Constraint category (required, length, format, etc.)
            error_description: Error description text
            field_name: Name of the field
            
        Returns:
            True if error matches constraint category
        """
        category_keywords = {
            "required": ["required", "missing", "must", "mandatory"],
            "length": ["length", "characters", "char", "min", "max"],
            "format": ["format", "pattern", "invalid", "malformed"],
            "range": ["range", "minimum", "maximum", "between"],
            "type": ["type", "invalid", "expected"],
            "enum": ["enum", "allowed", "valid values"],
        }
        
        keywords = category_keywords.get(category.lower(), [])
        
        # Check if any keyword appears in error description
        return any(keyword in error_description for keyword in keywords)
