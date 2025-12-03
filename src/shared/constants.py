"""Constantes centralizadas para eliminar valores hardcoded.

Este módulo consolida todas las constantes del proyecto en un solo lugar
para facilitar mantenimiento y evitar duplicación.
"""
from typing import Set


class VersionInfo:
    """Información de versiones del proyecto."""
    TOOL_VERSION = "1.0.0"
    API_VERSION = "v1"
    MIN_PYTHON_VERSION = "3.13"


class HTTPStatus:
    """Códigos de estado HTTP y sus categorías."""
    
    # Success codes (2xx)
    SUCCESS_CODES: Set[int] = {200, 201, 204}
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    
    # Client error codes (4xx)
    CLIENT_ERROR_START = 400
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    
    # Server error codes (5xx)
    SERVER_ERROR_START = 500
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    
    @staticmethod
    def is_success(status_code: int) -> bool:
        """Verifica si un código de estado es exitoso."""
        return status_code in HTTPStatus.SUCCESS_CODES
    
    @staticmethod
    def is_client_error(status_code: int) -> bool:
        """Verifica si un código de estado es error del cliente."""
        return 400 <= status_code < 500
    
    @staticmethod
    def is_server_error(status_code: int) -> bool:
        """Verifica si un código de estado es error del servidor."""
        return status_code >= 500


class JSONConfig:
    """Configuración estándar para operaciones JSON."""
    INDENT = 2
    ENSURE_ASCII = False
    ENCODING = 'utf-8'


class FileExtensions:
    """Extensiones de archivos soportadas."""
    JSON = ".json"
    YAML = ".yaml"
    YML = ".yml"
    FEATURE = ".feature"
    JAVASCRIPT = ".js"


class OutputPaths:
    """Paths relativos para outputs del proyecto."""
    BASE_OUTPUT = "output"
    SWAGGER_OUTPUT = "swagger"
    TEST_CASES_OUTPUT = "test_cases"
    BVA_OUTPUT = "bva_tests"
    FUNCTIONAL_OUTPUT = "functional"
    FEATURES_OUTPUT = "resources/features"
    LOGS_OUTPUT = "logs"


class TestingTechniques:
    """Nombres de técnicas de testing ISTQB v4."""
    EQUIVALENCE_PARTITIONING = "Equivalence Partitioning"
    BOUNDARY_VALUE_ANALYSIS = "Boundary Value Analysis"
    STATUS_CODE_COVERAGE = "Status Code Coverage"
    DECISION_TABLE = "Decision Table"
    STATE_TRANSITION = "State Transition"
    
    # Versiones de BVA
    BVA_2_VALUE = "2-value"
    BVA_3_VALUE = "3-value"
    BVA_BOTH = "both"
    
    VALID_BVA_VERSIONS = {BVA_2_VALUE, BVA_3_VALUE, BVA_BOTH}


class TestPriorities:
    """Prioridades de test cases."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    VALID_PRIORITIES = {HIGH, MEDIUM, LOW}


class KarateTags:
    """Tags estándar para features de Karate."""
    SMOKE = "@smoke"
    REGRESSION = "@regression"
    POSITIVE = "@positive"
    NEGATIVE = "@negative"
    
    # Tags por método HTTP
    GET = "@get"
    POST = "@post"
    PUT = "@put"
    DELETE = "@delete"
    PATCH = "@patch"
    
    @staticmethod
    def for_http_method(method: str) -> str:
        """Retorna el tag apropiado para un método HTTP."""
        return f"@{method.lower()}"
    
    @staticmethod
    def for_status_code(status: int) -> str:
        """Retorna el tag apropiado para un código de estado."""
        return f"@status{status}"


class ErrorPrefixes:
    """Prefijos estándar para códigos de error."""
    HEADER = "HDR"
    REQUEST_BODY_VALIDATION = "RBV"
    PATH_PARAMETER = "PPV"
    QUERY_PARAMETER = "QPV"
    BUSINESS_LOGIC = "BL"
    AUTHENTICATION = "AUTH"
    AUTHORIZATION = "AUTHZ"


class ValidationPatterns:
    """Patrones regex comunes para validación."""
    UUID_PATTERN = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    IPV4_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$'
    URL_PATTERN = r'^https?://.+'


class DefaultValues:
    """Valores por defecto para diversos componentes."""
    
    # HTTP
    HTTP_TIMEOUT = 30
    MAX_CONNECTIONS = 10
    
    # API
    DEFAULT_BASE_URL = "http://localhost:8080"
    DEFAULT_PROTOCOL = "http"
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 8080
    
    # UUID estándar
    VALID_UUID_EXAMPLE = "550e8400-e29b-41d4-a716-446655440000"
    UUID_LENGTH = 36
    
    # Límites
    STRING_MIN_LENGTH = 1
    STRING_MAX_LENGTH = 255
    MAX_SPEC_SIZE_MB = 10.0
    
    # Cache
    CACHE_TTL_SECONDS = 3600  # 1 hora


class LoggingConfig:
    """Configuración de logging."""
    DEFAULT_LEVEL = "INFO"
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_LOG_FILE = "mcp_swagger.log"
    
    VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


# Constantes para compatibilidad con código existente
TOOL_VERSION = VersionInfo.TOOL_VERSION
SUCCESS_STATUS_CODES = HTTPStatus.SUCCESS_CODES
JSON_INDENT = JSONConfig.INDENT
JSON_ENSURE_ASCII = JSONConfig.ENSURE_ASCII
