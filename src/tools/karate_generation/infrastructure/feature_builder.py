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
            "@api"
        ]
        return " ".join(tags)
    
    def _build_feature_description(self, feature: KarateFeature) -> str:
        """Build feature description section."""
        return f"Feature: {feature.feature_name}"
    
    def _build_background(self, feature: KarateFeature) -> str:
        """Build background section with centralized header configuration."""
        lines = ["Background:"]
        
        # Use centralized baseUrl from config
        lines.append(f"{self.indent}Given url baseUrl")
        
        # Build headers using centralized config function with automatic UUID generation
        lines.append(f"{self.indent}* def configHeader = karate.call('classpath:karate-config.js').buildHeaders({{}})")
        
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
        
        # All headers now come from buildHeaders() - this method is deprecated
        # Kept for backward compatibility only
        return f"{self.indent}# Header '{header_name}' managed by buildHeaders()"
    
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
        
        # Build dynamic path using Karate path() method
        if "{" in feature.endpoint:
            path_parts = self._build_dynamic_path(feature.endpoint)
            steps.append(f"{indent}Given path {path_parts}")
            
            # Extract path params for Examples table usage
            path_params = self._extract_path_params(feature.endpoint)
            for param in path_params:
                steps.append(f"{indent}* def {param} = '<{param}>'")
        else:
            # Static path
            steps.append(f"{indent}Given path '{feature.endpoint}'")
        
        # Add conditional header manipulation for header validation tests
        if is_header_validation and scenario.scenario_type == ScenarioType.NEGATIVE:
            # Copy valid headers first
            steps.append(f"{indent}* def headers = configHeader")
            
            # Check if this is type validation (has invalidValue) or required validation (missing header)
            has_invalid_value = any('invalidValue' in ex.to_table_row() for ex in scenario.examples)
            
            if has_invalid_value:
                # Type validation: set invalid value
                steps.append(f"{indent}* headers['<headerName>'] = <invalidValue>")
            else:
                # Required validation: remove header
                steps.append(f"{indent}* remove headers.<headerName>")
            
            # Apply modified headers
            steps.append(f"{indent}And headers headers")
        else:
            # Apply headers normally
            steps.append(f"{indent}And headers configHeader")
        
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
        
        # Response validation based on scenario type and status
        if scenario.scenario_type == ScenarioType.POSITIVE:
            # Positive scenarios: validate successful response structure
            steps.append(f"{indent}And match response != null")
            steps.append(f"{indent}And match response == '#object'")
        elif not is_header_validation:
            # Negative scenarios: validate error response structure
            expected_status = scenario.examples[0].expected_status if scenario.examples else 400
            
            if expected_status >= 400 and expected_status < 500:
                # Client errors: expect error structure
                steps.append(f"{indent}And match response != null")
                steps.append(f"{indent}And match response == '#object'")
                # Common error fields validation
                steps.append(f"{indent}And match response contains any {{ error: '#present', message: '#present', code: '#present' }}")
            elif expected_status >= 500:
                # Server errors: may have different structure
                steps.append(f"{indent}And match response != null")
        
        return steps
    
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
        """Build examples table with proper alignment, excluding unnecessary columns."""
        if not examples:
            return []
        
        # Get all unique column names from all examples
        all_columns = set()
        for example in examples:
            row = example.to_table_row()
            all_columns.update(row.keys())
        
        # Filter columns: keep only those with at least one non-empty value
        columns_with_values = set()
        for col in all_columns:
            for example in examples:
                row = example.to_table_row()
                value = str(row.get(col, "")).strip()
                if value:  # Column has at least one non-empty value
                    columns_with_values.add(col)
                    break
        
        # Order columns: standard fields first, then test data
        standard_fields = self._get_standard_column_order(columns_with_values)
        columns = [col for col in standard_fields if col in columns_with_values]
        
        # Add remaining columns in sorted order
        remaining_cols = sorted(columns_with_values - set(columns))
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
    
    def _build_dynamic_path(self, endpoint: str) -> str:
        """Build dynamic path string for Karate.
        
        Converts: /polizas/{numeroPoliza}/descargar
        To: '/polizas', numeroPoliza, '/descargar'
        """
        import re
        
        # Split by path parameters
        parts = re.split(r'(\{[^}]+\})', endpoint)
        
        path_elements = []
        for part in parts:
            if not part:
                continue
            
            if part.startswith('{') and part.endswith('}'):
                # Path parameter - use variable name
                param_name = part[1:-1]
                path_elements.append(param_name)
            else:
                # Static path segment
                path_elements.append(f"'{part}'")
        
        return ", ".join(path_elements)
    
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