"""
Builder for Karate feature file content using Gherkin syntax.
"""
from typing import List, Dict, Any
from ..domain.models import (
    KarateFeature, 
    KarateScenario, 
    KarateExample,
    ScenarioType,
    HttpMethod
)


class KarateFeatureBuilder:
    """Builds Karate feature file content with proper Gherkin syntax."""
    
    def __init__(self):
        self.indent = "  "  # 2 spaces for Gherkin indentation
    
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
            "@regression",
            f"@{feature.http_method.value.lower()}",
            f"@{feature.get_feature_path()}"
        ]
        return " ".join(tags)
    
    def _build_feature_description(self, feature: KarateFeature) -> str:
        """Build feature description section."""
        lines = [
            f"Feature: {feature.feature_name}",
            "",
            f"{self.indent}Automated tests for {feature.http_method.value} {feature.endpoint}",
            f"{self.indent}Generated from equivalence partitioning test cases",
            "",
            f"{self.indent}Total test cases: {feature.total_test_cases}",
            f"{self.indent}Success scenarios: {feature.success_count}",
            f"{self.indent}Failure scenarios: {feature.failure_count}"
        ]
        return "\n".join(lines)
    
    def _build_background(self, feature: KarateFeature) -> str:
        """Build background section with common setup."""
        lines = [
            "Background:",
            f"{self.indent}* url baseUrl",
            f"{self.indent}* def commonHeaders = getCommonHeaders()",
            f"{self.indent}* configure headers = commonHeaders"
        ]
        
        # Add path parameters if needed
        if "{" in feature.endpoint:
            lines.append(f"{self.indent}# Path parameters will be set in scenarios")
        
        return "\n".join(lines)
    
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
        
        # Given: Setup test data
        steps.append(f"{indent}Given path '{feature.endpoint}'")
        
        # Set path parameters if needed
        if "{" in feature.endpoint:
            path_params = self._extract_path_params(feature.endpoint)
            for param in path_params:
                steps.append(f"{indent}And param {param} = <{param}>")
        
        # Set headers (override if needed for negative tests)
        if scenario.scenario_type == ScenarioType.NEGATIVE:
            steps.append(f"{indent}And header x-correlation-id = <xCorrelationId>")
            steps.append(f"{indent}And header x-request-id = <xRequestId>")
            steps.append(f"{indent}And header x-transaction-id = <xTransactionId>")
        
        # Set request body for POST/PUT/PATCH
        if feature.http_method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
            steps.append(f"{indent}And request <requestBody>")
        
        # When: Execute request
        steps.append(f"{indent}When method {feature.http_method.value}")
        
        # Then: Validate response
        steps.append(f"{indent}Then status <expectedStatus>")
        
        if scenario.scenario_type == ScenarioType.POSITIVE:
            steps.append(f"{indent}And match response != null")
            steps.append(f"{indent}And match responseType == 'json'")
        else:
            steps.append(f"{indent}And match response.error != null")
            if any(ex.expected_error for ex in scenario.examples):
                steps.append(f"{indent}And match response.error.code == '<expectedError>'")
        
        return steps
    
    def _build_examples_table(self, examples: List[KarateExample]) -> List[str]:
        """Build examples table with proper alignment."""
        if not examples:
            return []
        
        # Get all unique column names from first example
        sample_row = examples[0].to_table_row()
        columns = list(sample_row.keys())
        
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
    
    def _extract_path_params(self, endpoint: str) -> List[str]:
        """Extract path parameter names from endpoint."""
        import re
        return re.findall(r'\{(\w+)\}', endpoint)
    
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