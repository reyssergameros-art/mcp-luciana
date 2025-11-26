"""Error code and validation error extractor from swagger descriptions."""
import re
from typing import Dict, Any, List

from ....shared.config import SwaggerConstants


class ErrorExtractor:
    """
    Responsible for extracting error codes and validation patterns from descriptions.
    
    Follows Single Responsibility Principle - only handles error extraction.
    """
    
    # Compile regex patterns once at class level for performance
    _ERROR_CODE_REGEX = re.compile(
        SwaggerConstants.ERROR_CODE_PATTERN, 
        re.DOTALL | re.IGNORECASE
    )
    _SUB_CODE_REGEX = re.compile(
        SwaggerConstants.SUB_CODE_PATTERN, 
        re.DOTALL
    )
    
    def __init__(self):
        """Initialize error extractor."""
        pass
    
    def extract_error_codes(self, description: str) -> List[Dict[str, Any]]:
        """
        Extract error codes and their details from description text.
        
        Looks for patterns like:
        *TYP-001* - type_error (HTTP 400) details...
        
        Args:
            description: Description text to analyze
            
        Returns:
            List of error code dictionaries with code, type, status, description, sub_codes
        """
        if not description:
            return []
        
        error_codes = []
        
        for match in self._ERROR_CODE_REGEX.finditer(description):
            code = match.group(1)
            error_type = match.group(2)
            http_status = match.group(3)
            details = match.group(4).strip()
            
            # Extract sub-codes from the error details
            sub_codes = self._extract_sub_codes(details)
            
            # Limit description length
            max_length = SwaggerConstants.MAX_DESCRIPTION_LENGTH
            truncated_details = details[:max_length] if details else ''
            
            error_codes.append({
                'code': code,
                'type': error_type,
                'http_status': int(http_status),
                'description': truncated_details,
                'sub_codes': sub_codes
            })
        
        return error_codes
    
    def _extract_sub_codes(self, error_block: str) -> List[Dict[str, Any]]:
        """
        Extract sub-error codes from an error block.
        
        Looks for patterns like:
        HDR-001: description text
        
        Args:
            error_block: Text block containing sub-codes
            
        Returns:
            List of sub-code dictionaries
        """
        if not error_block:
            return []
        
        sub_codes = []
        max_length = SwaggerConstants.MAX_ERROR_DESCRIPTION_LENGTH
        
        for match in self._SUB_CODE_REGEX.finditer(error_block):
            sub_code = match.group(1)
            description = match.group(2).strip()
            
            # Limit description length
            truncated_description = description[:max_length] if description else ''
            
            sub_codes.append({
                'code': sub_code,
                'description': truncated_description
            })
        
        return sub_codes
    
    def extract_validation_errors(self, description: str) -> List[Dict[str, Any]]:
        """
        Extract validation error information from description.
        
        Searches for common validation error patterns like:
        - "required field"
        - "minimum length"
        - "must match pattern"
        
        Args:
            description: Description text to analyze
            
        Returns:
            List of validation error dictionaries
        """
        if not description:
            return []
        
        validation_errors = []
        
        for error_type, pattern in SwaggerConstants.VALIDATION_PATTERNS.items():
            if re.search(pattern, description, re.IGNORECASE):
                validation_errors.append({
                    'type': error_type,
                    'pattern_found': pattern
                })
        
        return validation_errors
    
    def extract_all_from_description(self, description: str) -> Dict[str, Any]:
        """
        Extract both error codes and validation errors from description.
        
        Args:
            description: Description text to analyze
            
        Returns:
            Dictionary with 'error_codes' and 'validation_errors' keys
        """
        return {
            'error_codes': self.extract_error_codes(description),
            'validation_errors': self.extract_validation_errors(description)
        }