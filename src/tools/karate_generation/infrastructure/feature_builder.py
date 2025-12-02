"""
Builder for Karate feature file content using Gherkin syntax.
"""
from typing import List, Dict, Any, Set
from ..domain.models import (
    KarateFeature, 
    KarateScenario, 
    KarateExample,
    ScenarioType,
    HttpMethod
)
from ..domain.value_objects import HeaderExtractor
from ..config import FEATURE_CONFIG


class KarateFeatureBuilder:
    """Builds Karate feature file content with proper Gherkin syntax."""
    
    def __init__(self):
        self.indent = " " * FEATURE_CONFIG.INDENT_SPACES
        self.config = FEATURE_CONFIG
    
    def build(self, feature: KarateFeature) -> str:
        """
        Build complete feature file content.
        
        Args:
            feature: KarateFeature model
            
        Returns:
            Complete feature file content as string
        """
        sections = [
            self._build_header(feature),
            self._build_feature_description(feature),
            self._build_background(feature),
            self._build_scenarios(feature)
        ]
        
        return "\n\n".join(filter(None, sections))
    
    def _build_header(self, feature: KarateFeature) -> str:
        """Build feature file header with tags."""
        tags = [
            self.config.REGRESSION_TAG,
            f"@{feature.http_method.value.lower()}"
        ]
        return " ".join(tags)
    
    def _build_feature_description(self, feature: KarateFeature) -> str:
        """Build feature description section."""
        return f"Feature: {feature.feature_name}"
    
    def _build_background(self, feature: KarateFeature) -> str:
        """Build background section with common setup."""
        from ..domain.value_objects import HeaderExtractor
        
        lines = ["Background:"]
        
        # Dynamically generate UUID variables for headers that need them
        detected_headers = self._extract_feature_headers(feature)
        uuid_headers = {h for h in detected_headers if HeaderExtractor.is_uuid_header(h)}
        
        for header_name in sorted(uuid_headers):
            var_name = self._to_camel_case(header_name)
            var_name_capitalized = f"random{var_name.replace('x', 'X', 1) if var_name.startswith('x') else var_name.capitalize()}"
            lines.append(f"{self.indent}* def {var_name_capitalized} = java.util.UUID.randomUUID().toString()")
        
        # Add path parameters defaults if needed
        if "{" in feature.endpoint:
            path_params = self._extract_path_params(feature.endpoint)
            for param in path_params:
                # Generate default value for path parameter
                lines.append(f"{self.indent}* def {param} = karate.get('{param}', '1')")
        
        lines.extend([
            f"{self.indent}Given url baseUrl",
            f"{self.indent}And path '{feature.endpoint}'",
            f"{self.indent}* def configHeader = headersDefaultEndpoint"
        ])
        
        # Dynamically detect and configure headers based on feature usage
        detected_headers = self._extract_feature_headers(feature)
        
        for header_name in detected_headers:
            header_config = self._get_header_config(header_name)
            lines.append(header_config)
        
        return "\n".join(lines)
    
    def _feature_uses_header(self, feature: KarateFeature, header_pattern: str) -> bool:
        """Check if feature uses a specific header."""
        for scenario in feature.scenarios:
            for example in scenario.examples:
                test_data = example.test_data
                for key in test_data.keys():
                    if header_pattern in key.lower():
                        return True
        return False
    
    def _extract_feature_headers(self, feature: KarateFeature) -> Set[str]:
        """Extract all unique headers used in feature."""
        from ..domain.value_objects import HeaderExtractor
        
        headers = set()
        for scenario in feature.scenarios:
            for example in scenario.examples:
                test_data = example.test_data
                for key in test_data.keys():
                    if HeaderExtractor.is_header_field(key):
                        headers.add(key.lower())
        return headers
    
    def _get_header_config(self, header_name: str) -> str:
        """Generate configuration line for a specific header."""
        from ..domain.value_objects import HeaderExtractor
        
        # Generate variable name (camelCase)
        var_name = self._to_camel_case(header_name)
        
        # Check if it's a UUID header
        if HeaderExtractor.is_uuid_header(header_name):
            # UUID headers use random generators
            generator_var = f"random{var_name.replace('x', 'X', 1) if var_name.startswith('x') else var_name.capitalize()}"
            return f"{self.indent}* configHeader['{header_name}'] = {generator_var}"
        elif 'authorization' in header_name.lower():
            # Authorization uses predefined variable
            return f"{self.indent}* configHeader['Authorization'] = authorization"
        else:
            # Other headers use their value from test data
            return f"{self.indent}* configHeader['{header_name}'] = karate.get('{var_name}', '')"
    
    def _build_scenarios(self, feature: KarateFeature) -> str:
        """Build all scenario outlines."""
        scenarios = []
        
        # Group scenarios by type
        positive_scenarios = [s for s in feature.scenarios if s.scenario_type == ScenarioType.POSITIVE]
        negative_scenarios = [s for s in feature.scenarios if s.scenario_type == ScenarioType.NEGATIVE]
        
        # Build positive scenarios first
        for scenario in positive_scenarios:
            scenarios.append(self._build_scenario_outline(scenario, feature))
        
        # Then negative scenarios grouped by HTTP status
        negative_by_status = self._group_scenarios_by_status(negative_scenarios)
        for status, scenarios_list in sorted(negative_by_status.items()):
            for scenario in scenarios_list:
                scenarios.append(self._build_scenario_outline(scenario, feature))
        
        return "\n\n".join(scenarios)
    
    def _build_scenario_outline(self, scenario: KarateScenario, feature: KarateFeature) -> str:
        """Build a single scenario outline."""
        lines = []
        
        # Tags
        tags = scenario.get_all_tags()
        lines.append(f"{' '.join(tags)}")
        
        # Scenario name
        lines.append(f"Scenario Outline: {scenario.name}")
        
        # Description if available
        if scenario.description:
            lines.append(f"{self.indent}# {scenario.description}")
        
        # Given-When-Then steps
        lines.extend(self._build_scenario_steps(scenario, feature))
        
        # Examples table
        lines.append("")
        lines.append(f"{self.indent}Examples:")
        lines.extend(self._build_examples_table(scenario.examples))
        
        return "\n".join(lines)
    
    def _build_scenario_steps(self, scenario: KarateScenario, feature: KarateFeature) -> List[str]:
        """Build Given-When-Then steps for scenario."""
        steps = []
        indent = self.indent
        
        # Detect if this is a header validation scenario
        is_header_validation = self._is_header_validation_scenario(scenario)
        
        # Set path parameters if needed
        if "{" in feature.endpoint:
            path_params = self._extract_path_params(feature.endpoint)
            for param in path_params:
                steps.append(f"{indent}* def {param} = '<{param}>'")
        
        # Add conditional header manipulation for header validation tests
        if is_header_validation and scenario.scenario_type == ScenarioType.NEGATIVE:
            steps.extend(self._build_header_manipulation_steps(indent))
        
        # Apply headers
        steps.append(f"{indent}* headers configHeader")
        
        # Set request body for POST/PUT/PATCH
        if feature.http_method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
            if is_header_validation:
                # For header validation, use a minimal valid body
                steps.append(f"{indent}And request {{}}")
            else:
                steps.append(f"{indent}And request <requestBody>")
        
        # When: Execute request
        steps.append(f"{indent}When method {feature.http_method.value}")
        
        # Then: Validate response
        # For header validation, use hardcoded status from first example
        if is_header_validation and scenario.examples:
            expected_status = scenario.examples[0].expected_status
            steps.append(f"{indent}Then status {expected_status}")
        else:
            steps.append(f"{indent}Then status <expectedStatus>")
        
        # Response validation based on scenario type
        if scenario.scenario_type == ScenarioType.POSITIVE:
            steps.append(f"{indent}And match response != null")
            steps.append(f"{indent}And match responseType == 'json'")
        elif not is_header_validation:
            steps.append(f"{indent}And match response.error != null")
        
        return steps
    
    def _build_header_manipulation_steps(self, indent: str) -> List[str]:
        """Build steps for conditional header manipulation."""
        return [
            f"{indent}* if ('<action>' == 'remove') karate.remove('configHeader', '<headerName>')",
            f"{indent}* if ('<action>' == 'null') configHeader['<headerName>'] = null"
        ]
    
    def _is_header_validation_scenario(self, scenario: KarateScenario) -> bool:
        """Check if scenario validates header requirements."""
        from ..domain.value_objects import HeaderExtractor
        
        # Check if test names contain header validation keywords
        if not scenario.examples:
            return False
        
        sample_name = scenario.examples[0].test_name
        detected_headers = HeaderExtractor.detect_header_hints_in_text(sample_name)
        return len(detected_headers) > 0
    
    def _build_examples_table(self, examples: List[KarateExample]) -> List[str]:
        """Build examples table with proper alignment."""
        if not examples:
            return []
        
        # Get all unique column names from all examples
        all_columns = set()
        for example in examples:
            row = example.to_table_row()
            all_columns.update(row.keys())
        
        # Order columns: standard fields first (detected from common patterns), then test data
        standard_fields = self._get_standard_column_order(all_columns)
        columns = [col for col in standard_fields if col in all_columns]
        
        # Add remaining columns in sorted order
        remaining_cols = sorted(all_columns - set(columns))
        columns.extend(remaining_cols)
        
        # Calculate column widths
        col_widths = {col: len(col) for col in columns}
        for example in examples:
            row = example.to_table_row()
            for col in columns:
                value = str(row.get(col, ""))
                col_widths[col] = max(col_widths[col], len(value))
        
        # Build header row
        header_cells = [col.ljust(col_widths[col]) for col in columns]
        header = f"{self.indent}  | {' | '.join(header_cells)} |"
        
        # Build data rows
        rows = [header]
        for example in examples:
            row_data = example.to_table_row()
            cells = [str(row_data.get(col, "")).ljust(col_widths[col]) for col in columns]
            row = f"{self.indent}  | {' | '.join(cells)} |"
            rows.append(row)
        
        return rows
    
    def _get_standard_column_order(self, all_columns: Set[str]) -> List[str]:
        """
        Determine standard column order dynamically based on column patterns.
        
        Args:
            all_columns: All available columns
            
        Returns:
            Ordered list of standard fields
        """
        # Define priority patterns for standard fields
        priority_patterns = [
            ('testId', lambda c: c.lower() in ['testid', 'test_id', 'id']),
            ('testName', lambda c: c.lower() in ['testname', 'test_name', 'name']),
            ('expectedStatus', lambda c: 'status' in c.lower() and 'expected' in c.lower()),
            ('expectedError', lambda c: 'error' in c.lower() and 'expected' in c.lower()),
            ('priority', lambda c: c.lower() == 'priority')
        ]
        
        standard_fields = []
        for preferred_name, matcher in priority_patterns:
            # Find matching column
            matched = [col for col in all_columns if matcher(col)]
            if matched:
                standard_fields.append(matched[0])
        
        return standard_fields
    
    def _extract_path_params(self, endpoint: str) -> List[str]:
        """Extract path parameter names from endpoint."""
        import re
        return re.findall(r'\{([^}]+)\}', endpoint)
    
    def _extract_dynamic_headers(self, examples: List[KarateExample]) -> Set[str]:
        """Extract header names dynamically from test examples."""
        if not examples:
            return set()
        
        # Get headers from first example's test data
        first_example = examples[0]
        headers = HeaderExtractor.extract_headers_from_test_data(first_example.test_data)
        return headers
    
    def _to_camel_case(self, header_name: str) -> str:
        """Convert header name to camelCase for variable naming."""
        # x-correlation-id -> xCorrelationId
        # x-request-id -> xRequestId
        parts = header_name.split('-')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    def _group_scenarios_by_status(self, scenarios: List[KarateScenario]) -> Dict[int, List[KarateScenario]]:
        """Group negative scenarios by HTTP status code."""
        groups: Dict[int, List[KarateScenario]] = {}
        
        for scenario in scenarios:
            # Get status from first example
            if scenario.examples:
                status = scenario.examples[0].expected_status
                if status not in groups:
                    groups[status] = []
                groups[status].append(scenario)
        
        return groups