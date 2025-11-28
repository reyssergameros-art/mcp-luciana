"""Shared domain exceptions for test generation (all techniques)."""


class TestGenerationError(Exception):
    """Base exception for all test generation errors."""
    
    def __init__(self, message: str):
        """
        Initialize test generation error.
        
        Args:
            message: Error message describing what went wrong
            
        Example:
            raise TestGenerationError("Failed to generate test cases")
        """
        self.message = message
        super().__init__(self.message)


class InvalidSwaggerAnalysisError(TestGenerationError):
    """
    Raised when swagger analysis JSON is invalid or missing required data.
    
    Use this when:
    - Input JSON structure doesn't match expected format
    - Required fields are missing from swagger analysis
    - Data types are incorrect
    
    Example:
        raise InvalidSwaggerAnalysisError("Missing 'endpoints' in swagger analysis")
    """
    pass