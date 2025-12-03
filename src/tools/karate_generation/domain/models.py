"""
Domain models for Karate feature generation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum


class ScenarioType(Enum):
    """Types of test scenarios."""
    POSITIVE = "positive"
    NEGATIVE = "negative"


class HttpMethod(Enum):
    """HTTP methods supported."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class KarateExample:
    """Represents a row in the Examples table of a Scenario Outline."""
    test_case_id: str
    test_name: str
    test_data: Dict[str, Any]
    expected_status: int
    expected_error: Optional[str]
    priority: str
    tags: List[str]
    partition_category: str
    # Header validation metadata (for negative tests)
    header_validation: Optional[Dict[str, str]] = None  # {"condition": "no está presente", "action": "remove", "headerName": "Authorization"}
    
    @staticmethod
    def get_http_status_description(status_code: int) -> str:
        """Convert HTTP status code to human-readable description."""
        status_map = {
            200: "Success",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Access Denied",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error"
        }
        return status_map.get(status_code, str(status_code))
    
    def get_short_test_id(self) -> str:
        """Generate a shorter, more readable test ID."""
        # Extract meaningful parts: method + endpoint + category
        import re
        # EPGETprioritiesvalid_all20251128_96 -> GET-PRI-001
        parts = self.test_case_id.split('_')
        if len(parts) > 0:
            base = parts[0][:15]  # Limit to 15 chars
            # Add sequence number if exists
            if len(parts) > 1 and parts[-1].isdigit():
                return f"{base}-{parts[-1]}"
            return base
        return self.test_case_id[:20]  # Fallback: first 20 chars
    
    def to_table_row(self) -> Dict[str, Any]:
        """Convert to table row format with only necessary columns."""
        from .test_data_filter import TestDataFilter
        
        # If this is a header validation test, only include the specific header info
        if self.header_validation:
            header_name = self.header_validation.get("headerName", "")
            row = {"headerName": header_name}
            
            # Extract header validation fields using TestDataFilter
            validation_fields = TestDataFilter.extract_header_validation_fields(
                self.test_data, header_name
            )
            row.update(validation_fields)
            
            return row
        
        # For non-header tests, start with minimal metadata
        row = {}
        
        # Always include expectedStatus (critical for validations)
        row["expectedStatus"] = self.expected_status
        
        # Add non-header fields from test_data using TestDataFilter
        filtered_data = TestDataFilter.exclude_headers(self.test_data)
        row.update(filtered_data)
        
        return row


@dataclass
class KarateScenario:
    """Represents a Karate Scenario Outline."""
    name: str
    tags: List[str]
    scenario_type: ScenarioType
    http_method: HttpMethod
    endpoint: str
    examples: List[KarateExample]
    description: Optional[str] = None
    
    def get_primary_tag(self) -> str:
        """Get the primary tag for this scenario."""
        if self.scenario_type == ScenarioType.POSITIVE:
            return "@smoke"
        return "@regression"
    
    def get_all_tags(self) -> List[str]:
        """Get all tags following Cucumber best practices."""
        tags = []
        
        # Add semantic tags based on scenario type
        if self.scenario_type == ScenarioType.POSITIVE:
            tags.extend(["@smoke", "@happy-path"])
        else:
            tags.append("@error")
            
            # Detect specific error type
            if self.examples:
                status = self.examples[0].expected_status
                if status == 400:
                    tags.append("@validation")
                elif status == 401:
                    tags.append("@authentication")
                elif status == 403:
                    tags.append("@authorization")
                elif status == 404:
                    tags.append("@not-found")
                elif status >= 500:
                    tags.append("@server-error")
        
        # Add custom tags (filter out generic ones)
        for tag in self.tags:
            if tag not in ["@negativeTest", "@status400", "@status401", "@status500"]:
                if tag not in tags:
                    tags.append(tag)
        
        # Add regression tag
        tags.append("@regression")
        
        return tags


@dataclass
class KarateFeature:
    """Represents a complete Karate feature file."""
    feature_name: str
    endpoint: str
    http_method: HttpMethod
    scenarios: List[KarateScenario]
    source_filename: Optional[str] = None
    background_headers: List[str] = field(default_factory=list)
    total_test_cases: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    def get_file_name(self) -> str:
        """Generate the feature file name from source filename or endpoint."""
        if self.source_filename:
            # Use the source filename, just change extension to .feature
            return self.source_filename.replace('.json', '.feature')
        
        # Fallback: generate from endpoint (shouldn't happen with proper mapping)
        safe_endpoint = self.endpoint.replace("/", "_").replace("{", "").replace("}", "")
        if safe_endpoint.startswith("_"):
            safe_endpoint = safe_endpoint[1:]
        return f"{self.http_method.value}_{safe_endpoint}.feature"


@dataclass
class KarateConfig:
    """Represents karate-config.js configuration."""
    base_url: str
    headers: Dict[str, str]
    timeout: int
    retry: int
    environments: Dict[str, str] = field(default_factory=dict)
    dynamic_headers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def generate_config_content(self) -> str:
        """Generate the karate-config.js content."""
        env_conditions = self._format_environment_conditions()
        
        return f"""function fn() {{
  var env = karate.env; // get system property 'karate.env'
  karate.log('karate.env system property was:', env);
  
  if (!env) {{
    env = 'dev';
  }}
  
  var config = {{
    baseUrl: '{self.base_url}',
    timeout: {self.timeout},
    retry: {self.retry}
  }};
  
  // Helper function to generate UUIDs using Karate native
  config.generateUUID = function() {{
    return karate.uuid();
  }};
  
  // Function to build request headers with automatic UUID generation
  config.buildHeaders = function(overrides) {{
    overrides = overrides || {{}};
    var headers = {{
{self._format_all_headers_for_build()}
    }};
    
    // Apply overrides
    for (var key in overrides) {{
      if (overrides[key] === null) {{
        delete headers[key];
      }} else {{
        headers[key] = overrides[key];
      }}
    }}
    
    return headers;
  }};
  
  // Environment specific configuration
{env_conditions}
  
  karate.configure('connectTimeout', config.timeout);
  karate.configure('readTimeout', config.timeout);
  karate.configure('retry', {{ count: config.retry, interval: 5000 }});
  
  return config;
}}"""
    
    def _format_headers(self) -> str:
        """Format headers for config file."""
        lines = []
        for key, value in self.headers.items():
            lines.append(f"    '{key}': '{value}'")
        return ",\n".join(lines)
    
    def _format_all_headers_for_build(self) -> str:
        """Format all headers for buildHeaders() function with automatic UUID generation."""
        from .value_objects import HeaderExtractor
        
        lines = []
        
        # Add all headers from swagger dynamically
        for header_name, metadata in sorted(self.dynamic_headers.items()):
            description = metadata.get("description", "")
            is_required = metadata.get("required", False)
            
            # Check if header requires UUID generation
            if HeaderExtractor.is_uuid_header(header_name, description):
                lines.append(f"      '{header_name}': config.generateUUID()")
            elif "value" in metadata:
                # Header has a default value from swagger (Content-Type, Accept)
                lines.append(f"      '{header_name}': '{metadata['value']}'")
            else:
                # Non-UUID headers: use environment variable or default value
                # Format: karate.properties['header.name'] || 'DEFAULT_VALUE'
                default_value = self._generate_default_header_value(header_name, is_required)
                env_var = self._header_to_env_var(header_name)
                lines.append(f"      '{header_name}': karate.properties['{env_var}'] || '{default_value}'")
        
        return ",\n".join(lines)
    
    def _header_to_env_var(self, header_name: str) -> str:
        """Convert header name to environment variable format."""
        # Transaccion-Id -> header.transaccion.id
        # Aplicacion-Id -> header.aplicacion.id
        return f"header.{header_name.lower().replace('-', '.')}"
    
    def _generate_default_header_value(self, header_name: str, is_required: bool) -> str:
        """Generate appropriate default value based on header name and requirement."""
        header_lower = header_name.lower()
        
        # Specific defaults based on header semantics
        if 'aplicacion' in header_lower or 'application' in header_lower:
            if 'id' in header_lower:
                return 'APP-DEFAULT-001'
            elif 'nombre' in header_lower or 'name' in header_lower:
                return 'Aplicacion-Prueba'
        
        if 'usuario' in header_lower or 'user' in header_lower:
            if 'id' in header_lower:
                return 'USR-DEFAULT-001'
        
        if 'servicio' in header_lower or 'service' in header_lower:
            if 'nombre' in header_lower or 'name' in header_lower:
                return 'Servicio-Prueba'
            elif 'consumidor' in header_lower:
                return 'Consumidor-Prueba'
        
        if 'subscription' in header_lower or 'key' in header_lower:
            return 'default-subscription-key-12345'
        
        # Generic defaults
        if is_required:
            return f"DEFAULT-{header_name.upper().replace('-', '_')}"
        
        return ''
    
    def _format_environment_conditions(self) -> str:
        """Format environment-specific URL conditions."""
        if not self.environments:
            return ""
        
        conditions = []
        for i, (env_name, env_url) in enumerate(self.environments.items()):
            condition_type = "if" if i == 0 else "else if"
            conditions.append(f"  {condition_type} (env === '{env_name}') {{\n    config.baseUrl = '{env_url}';\n  }}")
        
        return "\n".join(conditions)


@dataclass
class KarateGenerationResult:
    """Result of Karate feature generation."""
    success: bool
    features_generated: List[str]
    config_file: str
    total_scenarios: int = 0
    total_examples: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "features_generated": self.features_generated,
            "config_file": self.config_file,
            "total_scenarios": self.total_scenarios,
            "total_examples": self.total_examples,
            "errors": self.errors
        }