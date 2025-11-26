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
    timeout: int = 30000
    retry: int = 0
    
    def generate_config_content(self) -> str:
        """Generate the karate-config.js content."""
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
  if (env === 'dev') {{
    config.baseUrl = 'http://localhost:8080';
  }} else if (env === 'qa') {{
    config.baseUrl = 'https://qa.example.com';
  }} else if (env === 'prod') {{
    config.baseUrl = 'https://api.example.com';
  }}
  
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


@dataclass
class TestRunnerTemplate:
    """Template for TestRunner.java file."""
    
    @staticmethod
    def generate_content() -> str:
        """Generate TestRunner.java content."""
        return """package karate.runner;

/**
 * TEMPLATE: Uncomment and configure when you set up your Java project with Karate dependencies.
 * 
 * Required Maven dependencies:
 * - com.intuit.karate:karate-junit5
 * - org.junit.jupiter:junit-jupiter-api
 * 
 * Required Gradle dependencies:
 * - testImplementation 'com.intuit.karate:karate-junit5:latest.version'
 * - testImplementation 'org.junit.jupiter:junit-jupiter-api:latest.version'
 */

/*
import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class TestRunner {
    
    @Test
    void testParallel() {
        Results results = Runner.path("classpath:resources/features")
                .tags("~@ignore")
                .parallel(5);
        assertEquals(0, results.getFailCount(), results.getErrorMessages());
    }
}
*/

public class TestRunner {
    // Uncomment the code above and remove this placeholder when ready
}
"""


@dataclass
class CucumberUtilTemplate:
    """Template for Cucumber.java utility file."""
    
    @staticmethod
    def generate_content() -> str:
        """Generate Cucumber.java content."""
        return """package karate.util;

/**
 * TEMPLATE: Uncomment and configure when you set up your Java project with Karate dependencies.
 * 
 * Required Maven dependencies:
 * - com.intuit.karate:karate-junit5
 * - net.masterthought:cucumber-reporting
 * - commons-io:commons-io
 * 
 * Required Gradle dependencies:
 * - testImplementation 'com.intuit.karate:karate-junit5:latest.version'
 * - testImplementation 'net.masterthought:cucumber-reporting:latest.version'
 * - testImplementation 'commons-io:commons-io:latest.version'
 */

/*
import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import net.masterthought.cucumber.Configuration;
import net.masterthought.cucumber.ReportBuilder;
import org.apache.commons.io.FileUtils;

public class Cucumber {

    public static void generateReport(String karateOutputPath) {
        Collection<File> jsonFiles = FileUtils.listFiles(new File(karateOutputPath), new String[]{"json"}, true);
        List<String> jsonPaths = new ArrayList<>(jsonFiles.size());
        jsonFiles.forEach(file -> jsonPaths.add(file.getAbsolutePath()));
        Configuration config = new Configuration(new File("target"), "karate-test");
        ReportBuilder reportBuilder = new ReportBuilder(jsonPaths, config);
        reportBuilder.generateReports();
    }
}
*/

public class Cucumber {
    // Uncomment the code above and remove this placeholder when ready
}
"""


@dataclass
class LogbackConfigTemplate:
    """Template for logback-test.xml file."""
    
    @staticmethod
    def generate_content() -> str:
        """Generate logback-test.xml content."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
  
    <appender name="FILE" class="ch.qos.logback.core.FileAppender">
        <file>target/karate.log</file>
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <logger name="com.intuit" level="DEBUG"/>
   
    <root level="info">
        <appender-ref ref="STDOUT" />
        <appender-ref ref="FILE" />
    </root>
    
</configuration>
"""


@dataclass
class KarateGenerationResult:
    """Result of Karate feature generation."""
    success: bool
    features_generated: List[str]
    config_file: str
    runner_file: Optional[str] = None
    util_file: Optional[str] = None
    logback_file: Optional[str] = None
    total_scenarios: int = 0
    total_examples: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "features_generated": self.features_generated,
            "config_file": self.config_file,
            "runner_file": self.runner_file,
            "util_file": self.util_file,
            "logback_file": self.logback_file,
            "total_scenarios": self.total_scenarios,
            "total_examples": self.total_examples,
            "errors": self.errors
        }