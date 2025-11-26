"""Domain exceptions for swagger analysis."""


class SwaggerAnalysisError(Exception):
    """
    Base exception for swagger analysis domain.
    
    All swagger analysis related exceptions inherit from this base class.
    Use this for generic error handling when you want to catch any
    swagger analysis error.
    
    Example:
        try:
            result = await service.analyze_swagger(url)
        except SwaggerAnalysisError as e:
            print(f"Swagger analysis failed: {e}")
    """
    pass


class InvalidSwaggerSpecError(SwaggerAnalysisError):
    """
    Raised when swagger specification is invalid or malformed.
    
    This exception is raised when the specification structure is incorrect,
    missing required fields, or contains invalid data types.
    
    Example:
        - Missing 'paths' section
        - Invalid JSON/YAML structure
        - Malformed endpoint definitions
    """
    pass


class SwaggerFetchError(SwaggerAnalysisError):
    """
    Raised when swagger specification cannot be fetched.
    
    This exception is raised when there are network issues, HTTP errors,
    file access problems, or timeout errors during spec retrieval.
    
    Example:
        - HTTP 404/500 errors
        - Network timeout
        - File not found
        - Permission denied
    """
    pass


class SwaggerParseError(SwaggerAnalysisError):
    """
    Raised when swagger specification cannot be parsed.
    
    This exception is raised when the specification can be fetched but
    cannot be correctly parsed or interpreted.
    
    Example:
        - Cannot resolve $ref references
        - Invalid schema definitions
        - Circular references
        - Unsupported OpenAPI extensions
    """
    pass


class UnsupportedSpecVersionError(SwaggerAnalysisError):
    """
    Raised when swagger/OpenAPI version is not supported.
    
    Currently supported versions:
        - Swagger 2.0
        - OpenAPI 3.x
    
    Example:
        - OpenAPI 1.x (too old)
        - OpenAPI 4.x (too new)
        - Missing version field
    """
    pass


class InvalidUrlError(SwaggerAnalysisError):
    """
    Raised when provided URL or file path is invalid.
    
    This exception is raised during initial URL/path validation before
    attempting to fetch the specification.
    
    Example:
        - Invalid URL format
        - File path doesn't exist
        - Path is not a file (is a directory)
        - Unsupported protocol
    """
    pass


class SpecSizeLimitExceededError(SwaggerAnalysisError):
    """
    Raised when specification file size exceeds the configured limit.
    
    This is a safety mechanism to prevent processing extremely large
    files that could cause memory or performance issues.
    
    Configure limit via: settings.max_spec_size_mb
    """
    pass


class EndpointLimitExceededError(SwaggerAnalysisError):
    """
    Raised when the number of endpoints exceeds the configured limit.
    
    This is a safety mechanism to prevent processing specifications with
    an excessive number of endpoints.
    
    Configure limit via: settings.max_endpoints_to_analyze
    """
    pass