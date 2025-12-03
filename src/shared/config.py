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
    TEST_TECHNIQUE_STATUS_CODE = "Status Code Coverage"
    TEST_TECHNIQUE_DT = "Decision Table"
    TEST_TECHNIQUE_ST = "State Transition"
    
    # Test case ID prefixes
    TEST_ID_PREFIX_EP = "EP"
    TEST_ID_PREFIX_BVA = "BVA"
    TEST_ID_PREFIX_SC = "SC"
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


from pathlib import Path
from dataclasses import dataclass


@dataclass
class OutputConfig:
    """Configuration for output directories and file formats."""
    
    # Base output directory
    BASE_OUTPUT_DIR: Path = Path("output")
    
    # Subdirectories
    SWAGGER_OUTPUT_DIR: str = "swagger"
    TEST_CASES_OUTPUT_DIR: str = "test_cases"
    BVA_OUTPUT_DIR: str = "bva_tests"
    FUNCTIONAL_OUTPUT_DIR: str = "functional"
    FEATURES_OUTPUT_DIR: str = "resources/features"
    
    # File formats
    JSON_INDENT: int = 2
    JSON_ENSURE_ASCII: bool = False
    
    def get_swagger_output_path(self) -> Path:
        """Get the full path for swagger output directory."""
        return self.BASE_OUTPUT_DIR / self.SWAGGER_OUTPUT_DIR
    
    def get_test_cases_output_path(self) -> Path:
        """Get the full path for test cases output directory."""
        return self.BASE_OUTPUT_DIR / self.TEST_CASES_OUTPUT_DIR
    
    def get_bva_output_path(self) -> Path:
        """Get the full path for BVA output directory."""
        return self.BASE_OUTPUT_DIR / self.BVA_OUTPUT_DIR
    
    def get_functional_output_path(self) -> Path:
        """Get the full path for functional tests output directory."""
        return self.BASE_OUTPUT_DIR / self.FUNCTIONAL_OUTPUT_DIR
    
    def get_features_output_path(self) -> Path:
        """Get the full path for Karate features output directory."""
        return self.get_functional_output_path() / self.FEATURES_OUTPUT_DIR


@dataclass
class APIConfig:
    """Configuration for API defaults."""
    
    DEFAULT_BASE_URL: str = "http://localhost:8080"
    DEFAULT_PROTOCOL: str = "http"
    DEFAULT_HOST: str = "localhost"
    DEFAULT_PORT: int = 8080
    
    VALID_PROTOCOLS: tuple = ("http", "https")
    
    def get_default_base_url(self) -> str:
        """Get the default base URL."""
        return self.DEFAULT_BASE_URL
    
    def validate_protocol(self, url: str) -> bool:
        """Validate if URL has valid protocol."""
        return any(url.startswith(f"{proto}://") for proto in self.VALID_PROTOCOLS)


@dataclass
class TestGenerationConfig:
    """Configuration for test generation."""
    
    # Default techniques
    DEFAULT_TECHNIQUES: list = None
    DEFAULT_BVA_VERSION: str = "both"
    
    # Valid values
    VALID_BVA_VERSIONS: tuple = ("2-value", "3-value", "both")
    VALID_TECHNIQUES: tuple = ("equivalence_partitioning", "boundary_value_analysis")
    
    # Tool version
    TOOL_VERSION: str = "1.0.0"
    
    def __post_init__(self):
        """Initialize default techniques after instance creation."""
        if self.DEFAULT_TECHNIQUES is None:
            self.DEFAULT_TECHNIQUES = [
                "equivalence_partitioning",
                "boundary_value_analysis"
            ]
    
    def get_default_techniques(self) -> list:
        """Get the default techniques list."""
        if self.DEFAULT_TECHNIQUES is None:
            return list(self.VALID_TECHNIQUES)
        return self.DEFAULT_TECHNIQUES
    
    def get_default_bva_version(self) -> str:
        """Get the default BVA version."""
        return self.DEFAULT_BVA_VERSION
    
    def validate_bva_version(self, version: str) -> bool:
        """Validate BVA version."""
        return version in self.VALID_BVA_VERSIONS
    
    def validate_technique(self, technique: str) -> bool:
        """Validate technique name."""
        return technique in self.VALID_TECHNIQUES


@dataclass
class SwaggerAnalysisConfig:
    """Configuration for Swagger analysis."""
    
    # Default formats
    DEFAULT_FORMAT: str = "detailed"
    DEFAULT_OUTPUT_FORMAT: str = "both"
    
    # Valid values
    VALID_FORMATS: tuple = ("detailed", "summary")
    VALID_OUTPUT_FORMATS: tuple = ("console", "file", "both")
    
    def get_default_format(self) -> str:
        """Get the default analysis format."""
        return self.DEFAULT_FORMAT
    
    def get_default_output_format(self) -> str:
        """Get the default output format."""
        return self.DEFAULT_OUTPUT_FORMAT
    
    def validate_format(self, format: str) -> bool:
        """Validate analysis format."""
        return format in self.VALID_FORMATS
    
    def validate_output_format(self, output_format: str) -> bool:
        """Validate output format."""
        return output_format in self.VALID_OUTPUT_FORMATS


class ConfigManager:
    """
    Central configuration manager following SOLID principles.
    Single Responsibility: Manages all configuration settings.
    """
    
    def __init__(
        self,
        output_config: Optional[OutputConfig] = None,
        api_config: Optional[APIConfig] = None,
        test_generation_config: Optional[TestGenerationConfig] = None,
        swagger_analysis_config: Optional[SwaggerAnalysisConfig] = None
    ):
        """
        Initialize configuration manager.
        Dependency Injection: Allows custom configurations to be injected.
        """
        self.output = output_config or OutputConfig()
        self.api = api_config or APIConfig()
        self.test_generation = test_generation_config or TestGenerationConfig()
        self.swagger_analysis = swagger_analysis_config or SwaggerAnalysisConfig()
    
    def get_output_config(self) -> OutputConfig:
        """Get output configuration."""
        return self.output
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration."""
        return self.api
    
    def get_test_generation_config(self) -> TestGenerationConfig:
        """Get test generation configuration."""
        return self.test_generation
    
    def get_swagger_analysis_config(self) -> SwaggerAnalysisConfig:
        """Get swagger analysis configuration."""
        return self.swagger_analysis


# Global configuration instance (can be overridden for testing)
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.
    Singleton pattern for configuration management.
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def set_config_manager(config_manager: ConfigManager) -> None:
    """
    Set a custom configuration manager (useful for testing).
    """
    global _config_manager
    _config_manager = config_manager


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