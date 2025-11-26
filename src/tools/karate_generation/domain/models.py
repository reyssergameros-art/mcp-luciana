"""
Domain models for Karate feature generation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
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
    
    def to_table_row(self) -> Dict[str, Any]:
        """Convert to table row format."""
        return {
            "testId": self.test_case_id,
            "testName": self.test_name,
            "expectedStatus": self.expected_status,
            "expectedError": self.expected_error or "N/A",
            "priority": self.priority,
            **self.test_data
        }


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
        """Get all tags including generated ones."""
        base_tags = [self.get_primary_tag()]
        base_tags.extend(self.tags)
        return list(set(base_tags))  # Remove duplicates


@dataclass
class KarateFeature:
    """Represents a complete Karate feature file."""
    feature_name: str
    endpoint: str
    http_method: HttpMethod
    scenarios: List[KarateScenario]
    background_headers: List[str] = field(default_factory=list)
    total_test_cases: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    def get_file_name(self) -> str:
        """Generate the feature file name."""
        # Convert endpoint to safe filename: /priorities/{id} -> priorities_id
        safe_endpoint = self.endpoint.replace("/", "_").replace("{", "").replace("}", "")
        if safe_endpoint.startswith("_"):
            safe_endpoint = safe_endpoint[1:]
        return f"{self.http_method.value}_{safe_endpoint}.feature"
    
    def get_feature_path(self) -> str:
        """Get the subdirectory for this feature based on endpoint."""
        # Extract base resource: /priorities/{id} -> priorities
        parts = [p for p in self.endpoint.split("/") if p and not p.startswith("{")]
        return parts[0] if parts else "api"


@dataclass
class KarateConfig:
    """Represents karate-config.js configuration."""
    base_url: str
    headers: Dict[str, str]
    timeout: int
    retry: int
    environments: Dict[str, str] = field(default_factory=dict)
    
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
  
  // Common headers
  config.headers = {{
{self._format_headers()}
  }};
  
  // Helper functions
  config.generateUUID = function() {{
    return java.util.UUID.randomUUID() + '';
  }};
  
  config.getCommonHeaders = function() {{
    return {{
      'x-correlation-id': config.generateUUID(),
      'x-request-id': config.generateUUID(),
      'x-transaction-id': config.generateUUID(),
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }};
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