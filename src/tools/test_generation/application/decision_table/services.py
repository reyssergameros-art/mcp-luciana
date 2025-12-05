"""
Application Service for Decision Table test generation (ISTQB v4).

Orchestrates the entire decision table test generation process following
the ISTQB v4 definition of Decision Table testing technique.

Responsibilities:
- Coordinate infrastructure components
- Load and validate Swagger analysis data
- Generate complete decision tables
- Build test cases from rules
- Calculate coverage metrics
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ...domain.decision_table.models import DecisionTableResult
from ...domain.decision_table.exceptions import DecisionTableError

# Infrastructure components
from ...infrastructure.decision_table.rule_identifier import RuleIdentifier
from ...infrastructure.decision_table.combination_generator import CombinationGenerator
from ...infrastructure.decision_table.action_resolver import DecisionTableActionResolver
from ...infrastructure.decision_table.table_builder import DecisionTableBuilder
from ...infrastructure.decision_table.test_case_builder import DecisionTableTestCaseBuilder

logger = logging.getLogger(__name__)


class DecisionTableService:
    """
    Application service for Decision Table test generation.
    
    Follows SOLID principles:
    - Single Responsibility: Orchestrates test generation workflow
    - Open/Closed: Easy to extend with new features
    - Dependency Inversion: Depends on abstractions (domain models)
    
    This service follows the same pattern as EquivalencePartitionService
    and BVAService for consistency across testing techniques.
    """
    
    def __init__(self):
        """
        Initialize service with infrastructure components.
        
        Uses Dependency Injection pattern for easy testing and extensibility.
        """
        self.rule_identifier = RuleIdentifier()
        self.combination_generator = CombinationGenerator()
        self.action_resolver = DecisionTableActionResolver()
        self.table_builder = DecisionTableBuilder()
        self.test_case_builder = DecisionTableTestCaseBuilder()
    
    async def generate_decision_table_tests(
        self,
        swagger_analysis_file: str,
        endpoint_filter: Optional[str] = None,
        method_filter: Optional[str] = None,
        minimize_table: bool = False
    ) -> List[DecisionTableResult]:
        """
        Generate Decision Table test cases from Swagger analysis.
        
        Args:
            swagger_analysis_file: Path to Swagger analysis JSON file
            endpoint_filter: Optional filter for specific endpoint
            method_filter: Optional filter for HTTP method
            minimize_table: Whether to minimize the decision table
            
        Returns:
            List of DecisionTableResult objects
            
        Raises:
            DecisionTableError: If generation fails
        """
        try:
            # Load Swagger analysis
            swagger_data = self._load_swagger_analysis(swagger_analysis_file)
            
            # Generate test cases for each endpoint
            results = []
            endpoints = swagger_data.get("analysis", {}).get("endpoints", [])
            
            for endpoint_data in endpoints:
                # Apply filters
                if endpoint_filter and endpoint_data.get("path") != endpoint_filter:
                    continue
                if method_filter and endpoint_data.get("method") != method_filter:
                    continue
                
                # Generate for this endpoint
                result = await self._generate_for_endpoint(
                    endpoint_data,
                    minimize_table
                )
                
                if result and result.test_cases:
                    results.append(result)
            
            logger.info(f"Generated Decision Table tests for {len(results)} endpoints")
            
            return results
            
        except Exception as e:
            raise DecisionTableError(
                f"Failed to generate Decision Table tests: {str(e)}"
            ) from e
    
    async def _generate_for_endpoint(
        self,
        endpoint_data: Dict[str, Any],
        minimize_table: bool
    ) -> Optional[DecisionTableResult]:
        """
        Generate Decision Table test cases for a single endpoint.
        
        Workflow:
        1. Identify conditions and actions from endpoint data
        2. Generate all feasible combinations of conditions
        3. Resolve actions for each combination
        4. Build decision table
        5. Generate test cases from rules
        6. Calculate metrics
        
        Args:
            endpoint_data: Endpoint data from Swagger analysis
            minimize_table: Whether to minimize the table
            
        Returns:
            DecisionTableResult or None if no tests generated
        """
        endpoint = endpoint_data.get("path", "")
        http_method = endpoint_data.get("method", "")
        
        try:
            logger.debug(f"Generating Decision Table for {http_method} {endpoint}")
            
            # Step 1: Identify conditions and actions
            conditions, actions = self.rule_identifier.identify_conditions_and_actions(
                endpoint_data
            )
            
            if not conditions or not actions:
                logger.warning(
                    f"No conditions or actions found for {http_method} {endpoint}"
                )
                return None
            
            # Step 2: Generate all feasible combinations
            combinations = self.combination_generator.generate_all_combinations(
                conditions,
                endpoint,
                http_method,
                minimize=minimize_table
            )
            
            if not combinations:
                logger.warning(
                    f"No feasible combinations found for {http_method} {endpoint}"
                )
                return None
            
            # Step 3: Resolve actions for each combination
            action_mappings = {}
            for combination in combinations:
                if combination["is_feasible"]:
                    rule_id = combination["rule_id"]
                    action_values = self.action_resolver.resolve_actions(
                        combination["condition_values"],
                        conditions,
                        actions
                    )
                    action_mappings[rule_id] = action_values
            
            # Step 4: Build decision table
            decision_table = self.table_builder.build_table(
                endpoint,
                http_method,
                conditions,
                actions,
                combinations,
                action_mappings
            )
            
            # Step 5: Generate test cases
            test_cases = self.test_case_builder.build_test_cases(decision_table)
            
            # Step 6: Create result with metrics
            result = DecisionTableResult(
                endpoint=endpoint,
                http_method=http_method,
                decision_table=decision_table,
                test_cases=test_cases
            )
            
            logger.info(
                f"Generated {len(test_cases)} test cases for {http_method} {endpoint} "
                f"(Coverage: {result.metrics.get('coverage_percentage', 0):.1f}%)"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Failed to generate Decision Table for {http_method} {endpoint}: {str(e)}",
                exc_info=True
            )
            raise DecisionTableError(
                f"Failed to generate for {http_method} {endpoint}: {str(e)}"
            ) from e
    
    def _load_swagger_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Load Swagger analysis from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Swagger analysis data
            
        Raises:
            DecisionTableError: If file cannot be loaded
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if "analysis" not in data:
                raise DecisionTableError("Invalid Swagger analysis format: missing 'analysis' key")
            
            return data
            
        except FileNotFoundError:
            raise DecisionTableError(f"Swagger analysis file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise DecisionTableError(f"Invalid JSON in file {file_path}: {str(e)}")
        except Exception as e:
            raise DecisionTableError(f"Failed to load Swagger analysis: {str(e)}")
