"""Domain models for swagger analysis."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class FieldFormat(Enum):
    """Enum for common field formats."""
    UUID = "uuid"
    DATE = "date"
    DATETIME = "date-time"
    EMAIL = "email"
    PHONE = "phone"
    PASSWORD = "password"
    URI = "uri"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    BINARY = "binary"
    BYTE = "byte"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT = "float"
    DOUBLE = "double"
    NONE = "none"


@dataclass
class ValidationConstraint:
    """Information about field validation constraints."""
    constraint_type: str  # e.g., "min_length", "max_length", "pattern", "enum", "range"
    value: Union[str, int, float, List]
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class FieldInfo:
    """Information about a field (header, request body field, etc.)."""
    name: str
    data_type: str
    required: bool
    format: FieldFormat
    description: Optional[str] = None
    example: Optional[Any] = None
    enum_values: Optional[List[str]] = None
    pattern: Optional[str] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    constraints: List[ValidationConstraint] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


@dataclass
class ResponseInfo:
    """Information about an API response."""
    status_code: str
    description: str
    content_type: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    example: Optional[Any] = None
    error_codes: List[Dict[str, Any]] = None  # List of error codes with details
    validation_errors: List[Dict[str, Any]] = None  # Validation error details
    
    def __post_init__(self):
        if self.error_codes is None:
            self.error_codes = []
        if self.validation_errors is None:
            self.validation_errors = []


@dataclass
class EndpointInfo:
    """Detailed information about an API endpoint."""
    method: str
    path: str
    summary: Optional[str] = None
    description: Optional[str] = None
    operation_id: Optional[str] = None
    tags: List[str] = None
    headers: List[FieldInfo] = None
    path_parameters: List[FieldInfo] = None
    query_parameters: List[FieldInfo] = None
    request_body: Optional[Dict[str, FieldInfo]] = None
    request_content_type: Optional[str] = None
    responses: List[ResponseInfo] = None
    validation_rules: Dict[str, Any] = None  # Global validation rules
    error_scenarios: List[Dict[str, Any]] = None  # Possible error scenarios

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.headers is None:
            self.headers = []
        if self.path_parameters is None:
            self.path_parameters = []
        if self.query_parameters is None:
            self.query_parameters = []
        if self.responses is None:
            self.responses = []
        if self.validation_rules is None:
            self.validation_rules = {}
        if self.error_scenarios is None:
            self.error_scenarios = []


@dataclass
class SwaggerAnalysisResult:
    """Complete result of swagger analysis."""
    base_urls: List[str]
    total_endpoints: int
    endpoints: List[EndpointInfo]
    title: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None
    license_info: Optional[Dict[str, str]] = None