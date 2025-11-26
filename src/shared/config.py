"""Configuration settings for the MCP Swagger Analysis server."""
from typing import Optional
from pydantic_settings import BaseSettings


class SwaggerConstants:
    """Constants for Swagger/OpenAPI parsing and validation."""
    
    # Supported versions
    OPENAPI_VERSION_PREFIX = "3."
    SWAGGER_VERSION_PREFIX = "2."
    OPENAPI_FIELD = "openapi"
    SWAGGER_FIELD = "swagger"
    
    # HTTP methods
    SUPPORTED_HTTP_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']
    
    # Content types
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_YAML_APP = "application/yaml"
    CONTENT_TYPE_YAML_TEXT = "text/yaml"
    
    # URL prefixes
    HTTP_PREFIX = "http://"
    HTTPS_PREFIX = "https://"
    FILE_PREFIX = "file://"
    
    # Spec fields
    FIELD_PATHS = "paths"
    FIELD_SERVERS = "servers"
    FIELD_HOST = "host"
    FIELD_SCHEMES = "schemes"
    FIELD_BASE_PATH = "basePath"
    FIELD_INFO = "info"
    FIELD_PARAMETERS = "parameters"
    FIELD_REQUEST_BODY = "requestBody"
    FIELD_RESPONSES = "responses"
    FIELD_CONTENT = "content"
    FIELD_SCHEMA = "schema"
    FIELD_PROPERTIES = "properties"
    FIELD_REQUIRED = "required"
    FIELD_REF = "$ref"
    
    # Parameter locations
    PARAM_IN_HEADER = "header"
    PARAM_IN_PATH = "path"
    PARAM_IN_QUERY = "query"
    
    # Schema constraints
    CONSTRAINT_MIN_LENGTH = "minLength"
    CONSTRAINT_MAX_LENGTH = "maxLength"
    CONSTRAINT_PATTERN = "pattern"
    CONSTRAINT_ENUM = "enum"
    CONSTRAINT_MINIMUM = "minimum"
    CONSTRAINT_MAXIMUM = "maximum"
    CONSTRAINT_TYPE = "type"
    CONSTRAINT_FORMAT = "format"
    CONSTRAINT_EXAMPLE = "example"
    CONSTRAINT_DESCRIPTION = "description"
    
    # Constraint types for ValidationConstraint
    CONSTRAINT_TYPE_MIN_LENGTH = "min_length"
    CONSTRAINT_TYPE_MAX_LENGTH = "max_length"
    CONSTRAINT_TYPE_PATTERN = "pattern"
    CONSTRAINT_TYPE_ENUM = "enum"
    CONSTRAINT_TYPE_MINIMUM = "minimum"
    CONSTRAINT_TYPE_MAXIMUM = "maximum"
    
    # Error extraction patterns
    ERROR_CODE_PATTERN = r'\\([A-Z]+-\d{3})\\\s*-\s*([a-z_]+)\s*\(HTTP\s+(\d{3})\)(.?)(?=\\[A-Z]+-\d{3}\\*|$)'
    SUB_CODE_PATTERN = r'([A-Z]+-\d{3}):\s*(.+?)(?=[A-Z]+-\d{3}:|$)'
    
    # Validation error patterns
    VALIDATION_PATTERNS = {
        'required_field': r'(?:required|must)\s+(?:field|be|have)',
        'min_length': r'(?:minimum|min)\s+(?:length|characters)',
        'max_length': r'(?:maximum|max)\s+(?:length|characters)',
        'pattern': r'(?:pattern|format|must match)',
        'unique': r'(?:unique|duplicate|already exists)',
        'range': r'(?:between|range|minimum|maximum)',
        'empty': r'(?:empty|null|blank|missing)',
        'type_mismatch': r'(?:type|invalid|expected)',
    }
    
    # Limits and boundaries
    MAX_DESCRIPTION_LENGTH = 200
    MAX_ERROR_DESCRIPTION_LENGTH = 150
    
    # Logging
    LOG_SEPARATOR_LENGTH = 60
    LOG_SEPARATOR_CHAR = "="
    
    # Test Generation Constants (ISTQB v4 Equivalence Partitioning)
    TEST_TECHNIQUE_EP = "Equivalence Partitioning"
    TEST_TECHNIQUE_BVA = "Boundary Value Analysis"
    TEST_TECHNIQUE_DT = "Decision Table"
    TEST_TECHNIQUE_ST = "State Transition"
    
    # Test case ID prefixes
    TEST_ID_PREFIX_EP = "EP"
    TEST_ID_PREFIX_BVA = "BVA"
    TEST_ID_PREFIX_DT = "DT"
    TEST_ID_PREFIX_ST = "ST"
    
    # Test data generation
    VALID_UUID_EXAMPLE = "550e8400-e29b-41d4-a716-446655440000"
    INVALID_UUID_EXAMPLES = ["invalid-uuid", "123", ""]
    UUID_LENGTH = 36  # Standard UUID v4 length with hyphens
    UUID_TOO_SHORT_EXAMPLE = "550e8400-e29b-41d4-a716"  # 25 chars (truncated)
    UUID_TOO_LONG_EXAMPLE = "550e8400-e29b-41d4-a716-446655440000-extra"  # 43 chars (with extra)
    
    VALID_EMAIL_EXAMPLE = "test@example.com"
    INVALID_EMAIL_EXAMPLES = ["invalid-email", "test@", "@example.com"]
    
    VALID_DATE_EXAMPLE = "2025-11-17"
    INVALID_DATE_EXAMPLES = ["2025-13-01", "invalid-date", ""]
    
    VALID_URI_EXAMPLE = "https://api.example.com/v1/resource"
    INVALID_URI_EXAMPLES = ["not-a-uri", "htp://invalid", "://missing-scheme", ""]
    
    VALID_IPV4_EXAMPLE = "192.168.1.1"
    INVALID_IPV4_EXAMPLES = ["256.1.1.1", "192.168", "invalid-ip", ""]
    
    VALID_IPV6_EXAMPLE = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    INVALID_IPV6_EXAMPLES = ["2001:0db8:85a3::8a2e::7334", "invalid-ipv6", ""]
    
    VALID_HOSTNAME_EXAMPLE = "api.example.com"
    INVALID_HOSTNAME_EXAMPLES = ["invalid_hostname", "-invalid.com", "too..many..dots", ""]
    
    # Partition boundaries
    BOUNDARY_OFFSET_BELOW = 1  # For testing below minimum
    BOUNDARY_OFFSET_ABOVE = 1  # For testing above maximum
    STRING_MIN_LENGTH_DEFAULT = 1
    STRING_MAX_LENGTH_DEFAULT = 255
    INTEGER_MIN_DEFAULT = -2147483648
    INTEGER_MAX_DEFAULT = 2147483647
    
    # Test priorities
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    
    # Coverage thresholds
    MIN_PARTITION_COVERAGE = 100.0  # ISTQB requires 100% partition coverage


class Settings(BaseSettings):
    """Application settings following SOLID principles (Single Responsibility)."""
    
    # HTTP settings
    http_timeout: int = 30
    max_connections: int = 10
    max_keepalive_connections: int = 5
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Analysis settings
    max_endpoints_to_analyze: Optional[int] = None  # None = no limit
    max_spec_size_mb: float = 10.0  # Maximum spec file size in MB
    enable_detailed_logging: bool = False
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    
    # Server settings
    server_name: str = "MCP-Swagger-Analysis"
    server_version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        env_prefix = "MCP_SWAGGER_"
        case_sensitive = False


# Singleton instance
settings = Settings()