"""Refactored HTTP Swagger Repository using specialized services."""
from typing import Dict, Any, List

from ..domain.repositories import SwaggerRepository
from ..domain.models import (
    SwaggerAnalysisResult, EndpointInfo, FieldInfo, ResponseInfo, FieldFormat
)
from ..domain.exceptions import (
    SwaggerParseError, UnsupportedSpecVersionError, EndpointLimitExceededError
)
from .fetcher import SwaggerFetcher
from .schema_resolver import SchemaResolver
from .error_extractor import ErrorExtractor
from .constraints_builder import ConstraintsBuilder
from .cache import SpecificationCache
from ....shared.config import settings, SwaggerConstants


class HttpSwaggerRepository(SwaggerRepository):
    """
    HTTP implementation of swagger repository.
    
    Now follows Single Responsibility Principle by delegating to specialized services.
    """
    
    def __init__(self, timeout: int = None):
        """
        Initialize repository with specialized services.
        
        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout or settings.http_timeout
        
        # Initialize specialized services
        self.fetcher = SwaggerFetcher(self.timeout)
        self.error_extractor = ErrorExtractor()
        self.constraints_builder = ConstraintsBuilder()
        self.cache = SpecificationCache()
        
        # Resolver is initialized per-spec since it needs the full spec
        self.resolver: SchemaResolver = None
    
    async def fetch_swagger_spec(self, url: str) -> Dict[str, Any]:
        """
        Fetch swagger specification from URL or file path with caching.
        
        Args:
            url: URL or file path to the swagger specification
            
        Returns:
            Parsed swagger specification dictionary
        """
        # Check cache first
        cached_spec = self.cache.get(url)
        if cached_spec is not None:
            return cached_spec
        
        # Fetch from source
        spec = await self.fetcher.fetch(url)
        
        # Cache the result
        self.cache.set(url, spec)
        
        return spec
    
    async def parse_swagger_spec(self, spec: Dict[str, Any]) -> SwaggerAnalysisResult:
        """
        Parse swagger specification into analysis result.
        
        Args:
            spec: Swagger specification dictionary
            
        Returns:
            SwaggerAnalysisResult with complete analysis
        """
        try:
            # Initialize resolver for this spec
            self.resolver = SchemaResolver(spec)
            
            # Validate spec version
            spec_version = self._validate_spec_version(spec)
            
            # Extract basic info
            info = spec.get(SwaggerConstants.FIELD_INFO, {})
            
            # Extract base URLs
            base_urls = self._extract_base_urls(spec)
            
            # Extract endpoints
            endpoints = self._extract_endpoints(spec)
            
            # Check endpoint limit
            if settings.max_endpoints_to_analyze is not None:
                if len(endpoints) > settings.max_endpoints_to_analyze:
                    raise EndpointLimitExceededError(
                        f"Number of endpoints ({len(endpoints)}) exceeds limit "
                        f"({settings.max_endpoints_to_analyze})"
                    )
            
            return SwaggerAnalysisResult(
                title=info.get('title'),
                version=info.get('version'),
                description=info.get(SwaggerConstants.CONSTRAINT_DESCRIPTION),
                contact_info=info.get('contact', {}),
                license_info=info.get('license', {}),
                base_urls=base_urls,
                total_endpoints=len(endpoints),
                endpoints=endpoints
            )
        except Exception as e:
            if isinstance(e, (UnsupportedSpecVersionError, EndpointLimitExceededError)):
                raise
            raise SwaggerParseError(f"Failed to parse swagger specification: {str(e)}") from e
    
    def _validate_spec_version(self, spec: Dict[str, Any]) -> str:
        """Validate and return spec version."""
        if SwaggerConstants.OPENAPI_FIELD in spec:
            version = spec[SwaggerConstants.OPENAPI_FIELD]
            if not version.startswith(SwaggerConstants.OPENAPI_VERSION_PREFIX):
                raise UnsupportedSpecVersionError(
                    f"OpenAPI version {version} not supported. Only 3.x is supported."
                )
            return f"OpenAPI {version}"
        elif SwaggerConstants.SWAGGER_FIELD in spec:
            version = spec[SwaggerConstants.SWAGGER_FIELD]
            if not version.startswith(SwaggerConstants.SWAGGER_VERSION_PREFIX):
                raise UnsupportedSpecVersionError(
                    f"Swagger version {version} not supported. Only 2.0 is supported."
                )
            return f"Swagger {version}"
        else:
            raise UnsupportedSpecVersionError(
                "Invalid spec: missing 'openapi' or 'swagger' version field"
            )
    
    def _extract_base_urls(self, spec: Dict[str, Any]) -> List[str]:
        """Extract base URLs from swagger spec."""
        base_urls = []
        
        # OpenAPI 3.x
        if SwaggerConstants.FIELD_SERVERS in spec:
            for server in spec[SwaggerConstants.FIELD_SERVERS]:
                base_urls.append(server.get('url', ''))
        
        # Swagger 2.0
        elif SwaggerConstants.FIELD_HOST in spec:
            schemes = spec.get(SwaggerConstants.FIELD_SCHEMES, ['http'])
            host = spec[SwaggerConstants.FIELD_HOST]
            base_path = spec.get(SwaggerConstants.FIELD_BASE_PATH, '')
            
            for scheme in schemes:
                base_urls.append(f"{scheme}://{host}{base_path}")
        
        return base_urls
    
    def _extract_endpoints(self, spec: Dict[str, Any]) -> List[EndpointInfo]:
        """Extract all endpoints from swagger spec."""
        endpoints = []
        paths = spec.get(SwaggerConstants.FIELD_PATHS, {})
        
        for path, path_item in paths.items():
            if isinstance(path_item, dict):
                for method, operation in path_item.items():
                    if method.lower() in SwaggerConstants.SUPPORTED_HTTP_METHODS:
                        endpoint = self._parse_endpoint(path, method, operation, spec)
                        endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_endpoint(
        self, 
        path: str, 
        method: str, 
        operation: Dict[str, Any], 
        spec: Dict[str, Any]
    ) -> EndpointInfo:
        """Parse a single endpoint operation."""
        endpoint = EndpointInfo(
            method=method.upper(),
            path=path,
            summary=operation.get('summary'),
            description=operation.get(SwaggerConstants.CONSTRAINT_DESCRIPTION),
            operation_id=operation.get('operationId'),
            tags=operation.get('tags', [])
        )
        
        # Parse parameters
        parameters = operation.get(SwaggerConstants.FIELD_PARAMETERS, [])
        for param in parameters:
            field_info = self._parse_parameter(param)
            
            param_location = param.get('in')
            if param_location == SwaggerConstants.PARAM_IN_HEADER:
                endpoint.headers.append(field_info)
            elif param_location == SwaggerConstants.PARAM_IN_PATH:
                endpoint.path_parameters.append(field_info)
            elif param_location == SwaggerConstants.PARAM_IN_QUERY:
                endpoint.query_parameters.append(field_info)
        
        # Parse request body (OpenAPI 3.x)
        if SwaggerConstants.FIELD_REQUEST_BODY in operation:
            endpoint.request_body, endpoint.request_content_type = self._parse_request_body(
                operation[SwaggerConstants.FIELD_REQUEST_BODY]
            )
        
        # Parse responses
        responses = operation.get(SwaggerConstants.FIELD_RESPONSES, {})
        for status_code, response_spec in responses.items():
            response_info = self._parse_response(status_code, response_spec)
            endpoint.responses.append(response_info)
        
        return endpoint
    
    def _parse_parameter(self, param: Dict[str, Any]) -> FieldInfo:
        """Parse a parameter into FieldInfo using ConstraintsBuilder."""
        name = param.get('name', '')
        required = param.get('required', False)
        description = param.get(SwaggerConstants.CONSTRAINT_DESCRIPTION, '')
        
        # Handle schema (OpenAPI 3.x) or direct type (Swagger 2.0)
        schema = param.get(SwaggerConstants.FIELD_SCHEMA, param)
        
        # Resolve $ref if present
        schema = self.resolver.resolve_if_ref(schema)
        
        data_type = schema.get(SwaggerConstants.CONSTRAINT_TYPE, 'string')
        format_str = schema.get(SwaggerConstants.CONSTRAINT_FORMAT, '')
        
        # Build constraints using ConstraintsBuilder
        constraints = self.constraints_builder.build_from_schema(schema)
        
        # Get field metadata
        metadata = self.constraints_builder.get_field_metadata(schema)
        
        return FieldInfo(
            name=name,
            data_type=data_type,
            required=required,
            format=self._parse_format(data_type, format_str),
            description=description,
            example=schema.get(SwaggerConstants.CONSTRAINT_EXAMPLE),
            enum_values=metadata['enum_values'],
            pattern=metadata['pattern'],
            minimum=metadata['minimum'],
            maximum=metadata['maximum'],
            min_length=metadata['min_length'],
            max_length=metadata['max_length'],
            constraints=constraints
        )
    
    def _parse_request_body(self, request_body: Dict[str, Any]) -> tuple:
        """Parse request body into field info dictionary."""
        content = request_body.get(SwaggerConstants.FIELD_CONTENT, {})
        
        for content_type, content_spec in content.items():
            schema = content_spec.get(SwaggerConstants.FIELD_SCHEMA, {})
            fields = self._parse_schema_properties(schema)
            return fields, content_type
        
        return None, None
    
    def _parse_schema_properties(self, schema: Dict[str, Any]) -> Dict[str, FieldInfo]:
        """Parse schema properties into field info dictionary."""
        fields = {}
        
        # Resolve $ref if present
        schema = self.resolver.resolve_if_ref(schema)
        
        properties = schema.get(SwaggerConstants.FIELD_PROPERTIES, {})
        required_fields = schema.get(SwaggerConstants.FIELD_REQUIRED, [])
        
        for field_name, field_schema in properties.items():
            # Resolve nested $ref
            field_schema = self.resolver.resolve_if_ref(field_schema)
            
            data_type = field_schema.get(SwaggerConstants.CONSTRAINT_TYPE, 'string')
            format_str = field_schema.get(SwaggerConstants.CONSTRAINT_FORMAT, '')
            
            # Build constraints using ConstraintsBuilder
            constraints = self.constraints_builder.build_from_schema(field_schema)
            
            # Get field metadata
            metadata = self.constraints_builder.get_field_metadata(field_schema)
            
            fields[field_name] = FieldInfo(
                name=field_name,
                data_type=data_type,
                required=field_name in required_fields,
                format=self._parse_format(data_type, format_str),
                description=field_schema.get(SwaggerConstants.CONSTRAINT_DESCRIPTION),
                example=field_schema.get(SwaggerConstants.CONSTRAINT_EXAMPLE),
                enum_values=metadata['enum_values'],
                pattern=metadata['pattern'],
                minimum=metadata['minimum'],
                maximum=metadata['maximum'],
                min_length=metadata['min_length'],
                max_length=metadata['max_length'],
                constraints=constraints
            )
        
        return fields
    
    def _parse_response(self, status_code: str, response_spec: Dict[str, Any]) -> ResponseInfo:
        """Parse a response specification using ErrorExtractor."""
        description = response_spec.get(SwaggerConstants.CONSTRAINT_DESCRIPTION, '')
        
        # Parse content (OpenAPI 3.x)
        content = response_spec.get(SwaggerConstants.FIELD_CONTENT, {})
        content_type = None
        schema = None
        example = None
        
        for ct, ct_spec in content.items():
            content_type = ct
            schema = ct_spec.get(SwaggerConstants.FIELD_SCHEMA, {})
            example = ct_spec.get(SwaggerConstants.CONSTRAINT_EXAMPLE) or schema.get(SwaggerConstants.CONSTRAINT_EXAMPLE)
            break  # Take the first content type
        
        # Fallback for Swagger 2.0
        if not content_type and SwaggerConstants.FIELD_SCHEMA in response_spec:
            schema = response_spec[SwaggerConstants.FIELD_SCHEMA]
            example = response_spec.get('examples')
        
        # Extract errors using ErrorExtractor
        extracted = self.error_extractor.extract_all_from_description(description)
        
        return ResponseInfo(
            status_code=status_code,
            description=description,
            content_type=content_type,
            schema=schema,
            example=example,
            error_codes=extracted['error_codes'],
            validation_errors=extracted['validation_errors']
        )
    
    def _parse_format(self, data_type: str, format_str: str) -> FieldFormat:
        """Parse data type and format into FieldFormat enum."""
        format_mapping = {
            'uuid': FieldFormat.UUID,
            'date': FieldFormat.DATE,
            'date-time': FieldFormat.DATETIME,
            'email': FieldFormat.EMAIL,
            'password': FieldFormat.PASSWORD,
            'uri': FieldFormat.URI,
            'ipv4': FieldFormat.IPV4,
            'ipv6': FieldFormat.IPV6,
            'binary': FieldFormat.BINARY,
            'byte': FieldFormat.BYTE,
            'int32': FieldFormat.INT32,
            'int64': FieldFormat.INT64,
            'float': FieldFormat.FLOAT,
            'double': FieldFormat.DOUBLE
        }
        
        # Check format first
        if format_str.lower() in format_mapping:
            return format_mapping[format_str.lower()]
        
        # Check for common patterns in field names or descriptions
        format_lower = format_str.lower()
        if any(keyword in format_lower for keyword in ['phone', 'mobile', 'cell']):
            return FieldFormat.PHONE
        
        return FieldFormat.NONE