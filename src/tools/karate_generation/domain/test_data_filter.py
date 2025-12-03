"""
Test data filtering utilities for Karate generation.
Extracts complex filtering logic to follow Single Responsibility Principle.
"""
from typing import Dict, Any, Set, Optional
from .value_objects import HeaderExtractor


class TestDataFilter:
    """
    Filters and transforms test data for Karate feature generation.
    Separates concerns of data filtering from domain models.
    
    Uses dynamic header detection from Swagger analysis instead of hardcoded patterns.
    """
    
    # Generic header patterns (protocol-level, not business-specific)
    GENERIC_HEADER_PATTERNS = {
        'starts_with': ['x-', 'X-'],
        'contains': ['-id', '-key', '-token', '-type', 'authorization', 'auth'],
        'standard_http': {
            'authorization', 'content-type', 'accept', 'user-agent', 
            'cache-control', 'connection', 'host', 'referer', 'origin'
        }
    }
    
    # Instance-level known headers (injected dynamically)
    _known_headers: Optional[Set[str]] = None
    
    @classmethod
    def configure(cls, known_headers: Set[str]):
        """
        Configure the filter with headers extracted from Swagger analysis.
        
        Args:
            known_headers: Set of header names found in the API specification
        """
        cls._known_headers = {h.lower() for h in known_headers}
    
    @classmethod
    def is_header_field(cls, field_name: str) -> bool:
        """
        Dynamically determine if a field represents a header.
        Uses multiple heuristics to avoid false positives/negatives.
        
        Priority:
        1. Known headers from Swagger (if configured)
        2. Standard HTTP headers
        3. Generic patterns (x-, -id, -key, etc.)
        4. HeaderExtractor fallback
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field is likely a header
        """
        field_lower = field_name.lower()
        
        # 1. Check against known headers from Swagger (highest priority)
        if cls._known_headers and field_lower in cls._known_headers:
            return True
        
        # 2. Check standard HTTP headers
        if field_lower in cls.GENERIC_HEADER_PATTERNS['standard_http']:
            return True
        
        # 3. Check generic starts_with patterns
        if any(field_name.startswith(prefix) or field_lower.startswith(prefix.lower()) 
               for prefix in cls.GENERIC_HEADER_PATTERNS['starts_with']):
            return True
        
        # 4. Check generic contains patterns with context (avoid false positives)
        for pattern in cls.GENERIC_HEADER_PATTERNS['contains']:
            if pattern in field_lower:
                # Additional context check: field should have header-like structure
                # e.g., has dashes or is compound word
                if '-' in field_name or field_name[0].isupper():
                    return True
        
        # 5. Use HeaderExtractor as final fallback
        return HeaderExtractor.is_header_field(field_name)
    
    @staticmethod
    def exclude_headers(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out header fields from test data.
        
        Args:
            test_data: Dictionary containing test data with potential headers
            
        Returns:
            Dictionary with only non-header fields that have actual values
        """
        filtered = {}
        
        for key, value in test_data.items():
            # Skip if it's a header field
            if TestDataFilter.is_header_field(key):
                continue
            
            # Skip if value is empty/null
            if value in [None, "", [], {}]:
                continue
            
            filtered[key] = value
        
        return filtered
    
    @staticmethod
    def extract_header_validation_fields(test_data: Dict[str, Any], header_name: str) -> Dict[str, Any]:
        """
        Extract only relevant fields for header validation tests.
        
        Args:
            test_data: Original test data
            header_name: Name of the header being validated
            
        Returns:
            Dictionary with only the header being tested (if it has a value)
        """
        result = {}
        
        # Only include the specific header if it has a non-null/non-empty value
        if header_name in test_data:
            value = test_data[header_name]
            if value not in [None, "", [], {}]:
                result['invalidValue'] = value
        
        return result
    
    @staticmethod
    def should_include_field(field_name: str, value: Any) -> bool:
        """
        Determine if a field should be included in the Examples table.
        
        Args:
            field_name: Name of the field
            value: Value of the field
            
        Returns:
            True if field should be included
        """
        # Exclude headers
        if TestDataFilter.is_header_field(field_name):
            return False
        
        # Exclude empty values
        if value in [None, "", [], {}]:
            return False
        
        return True
    
    @staticmethod
    def get_metadata_fields() -> Set[str]:
        """
        Get standard metadata field names that should appear first in tables.
        
        Returns:
            Set of metadata field names
        """
        return {
            'testId', 'test_id', 'id',
            'testName', 'test_name', 'name',
            'expectedStatus', 'expected_status', 'status',
            'expectedError', 'expected_error', 'error',
            'priority'
        }
