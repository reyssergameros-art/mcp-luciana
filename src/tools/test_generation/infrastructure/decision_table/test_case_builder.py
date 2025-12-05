"""
Test Case Builder for Decision Table technique (ISTQB v4).

Converts decision rules into executable test cases with actual test data.
Generates UnifiedTestCase objects compatible with the rest of the system.
"""
from typing import List, Dict, Any
import logging

from ...domain.decision_table.models import (
    DecisionTable,
    DecisionRule,
    DecisionTableTestCase,
    DecisionCondition,
    DecisionAction,
    ConditionType,
    ConditionValue,
    ActionValue
)
from ...domain.decision_table.exceptions import DecisionTableError
from src.shared.constants import TestingTechniques, TestPriorities

logger = logging.getLogger(__name__)


class DecisionTableTestCaseBuilder:
    """
    Builds test cases from decision table rules.
    
    Respects SOLID principles:
    - Single Responsibility: Only builds test cases
    - Open/Closed: Extensible for new test data generation logic
    - Dependency Inversion: Works with domain models
    
    Responsibilities:
    - Convert DecisionRule to DecisionTableTestCase
    - Generate actual test data based on condition values
    - Build test case metadata and descriptions
    """
    
    def __init__(self):
        """Initialize test case builder."""
        self.test_case_counter = 0
    
    def build_test_cases(
        self,
        decision_table: DecisionTable
    ) -> List[DecisionTableTestCase]:
        """
        Build test cases from all feasible rules in the decision table.
        
        Args:
            decision_table: Complete DecisionTable object
            
        Returns:
            List of DecisionTableTestCase objects
            
        Raises:
            DecisionTableError: If test case generation fails
        """
        try:
            test_cases = []
            self.test_case_counter = 0
            
            # Only generate test cases for feasible rules
            feasible_rules = decision_table.get_feasible_rules()
            
            for rule in feasible_rules:
                test_case = self._build_test_case_from_rule(
                    rule,
                    decision_table.conditions,
                    decision_table.actions,
                    decision_table.endpoint,
                    decision_table.http_method
                )
                test_cases.append(test_case)
            
            logger.info(
                f"Built {len(test_cases)} test cases for {decision_table.http_method} "
                f"{decision_table.endpoint}"
            )
            
            return test_cases
            
        except Exception as e:
            raise DecisionTableError(
                f"Failed to build test cases: {str(e)}"
            ) from e
    
    def _build_test_case_from_rule(
        self,
        rule: DecisionRule,
        conditions: List[DecisionCondition],
        actions: List[DecisionAction],
        endpoint: str,
        http_method: str
    ) -> DecisionTableTestCase:
        """
        Build a single test case from a decision rule.
        
        Args:
            rule: DecisionRule to convert
            conditions: List of all conditions
            actions: List of all actions
            endpoint: API endpoint
            http_method: HTTP method
            
        Returns:
            DecisionTableTestCase object
        """
        self.test_case_counter += 1
        
        # Build condition lookup
        condition_map = {c.condition_id: c for c in conditions}
        action_map = {a.action_id: a for a in actions}
        
        # Generate test data from condition values
        test_data = self._generate_test_data(rule.condition_values, condition_map)
        
        # Find the action that should execute
        expected_action = self._find_executing_action(rule.action_values, action_map)
        
        # Build test case ID and name
        test_case_id = f"DT_{http_method}_{self._sanitize_name(endpoint)}_{rule.rule_id}"
        test_name = self._generate_test_name(rule, condition_map, expected_action)
        
        # Build objective
        objective = self._generate_objective(rule, condition_map, expected_action)
        
        # Build condition and action summaries
        condition_summary = self._build_condition_summary(rule.condition_values, condition_map)
        action_summary = self._build_action_summary(rule.action_values, action_map)
        
        # Determine priority
        priority = self._determine_priority(rule, expected_action)
        
        # Build tags
        tags = self._generate_tags(rule, expected_action)
        
        return DecisionTableTestCase(
            test_case_id=test_case_id,
            test_name=test_name,
            rule_id=rule.rule_id,
            endpoint=endpoint,
            http_method=http_method,
            test_data=test_data,
            expected_status_code=expected_action.expected_status_code if expected_action else 200,
            expected_error=expected_action.expected_error if expected_action else None,
            priority=priority,
            objective=objective,
            condition_summary=condition_summary,
            action_summary=action_summary,
            tags=tags,
            metadata={
                "technique": TestingTechniques.DECISION_TABLE,
                "rule_id": rule.rule_id,
                "is_feasible": rule.is_feasible
            }
        )
    
    def _generate_test_data(
        self,
        condition_values: Dict[str, Any],
        condition_map: Dict[str, DecisionCondition]
    ) -> Dict[str, Any]:
        """
        Generate actual test data from condition values.
        
        Args:
            condition_values: Dictionary of condition_id -> value
            condition_map: Lookup of condition_id -> DecisionCondition
            
        Returns:
            Dictionary of field_name -> test_value
        """
        test_data = {}
        
        # Group by field name to avoid duplicates
        field_values = {}
        
        for cond_id, value in condition_values.items():
            condition = condition_map.get(cond_id)
            if not condition:
                continue
            
            field_name = condition.field_name
            
            # Generate actual value for this condition
            actual_value = self._generate_actual_value(value, condition)
            
            # Store the value (later values for same field override earlier ones)
            if actual_value is not None:
                field_values[field_name] = actual_value
        
        # Build final test data
        for field_name, value in field_values.items():
            test_data[field_name] = value
        
        return test_data
    
    def _generate_actual_value(
        self,
        condition_value: Any,
        condition: DecisionCondition
    ) -> Any:
        """
        Generate actual test value for a condition value.
        
        Args:
            condition_value: The condition value (T/F/– or extended value)
            condition: The DecisionCondition definition
            
        Returns:
            Actual value to use in test data
        """
        # Handle limited entry (boolean)
        if isinstance(condition_value, ConditionValue):
            if condition_value == ConditionValue.TRUE:
                return self._generate_valid_value(condition)
            elif condition_value == ConditionValue.FALSE:
                return self._generate_invalid_value(condition)
            elif condition_value == ConditionValue.IRRELEVANT:
                return self._generate_valid_value(condition)
            else:  # N/A
                return None
        
        # Handle extended entry
        if isinstance(condition_value, str):
            # Check for special markers
            if condition_value == "valid_length" or condition_value == "valid_range":
                return self._generate_valid_value(condition)
            elif "invalid" in condition_value.lower():
                return self._generate_invalid_value(condition)
            elif condition_value.startswith("length<"):
                # Too short
                return self._generate_too_short_value(condition)
            elif condition_value.startswith("length>"):
                # Too long
                return self._generate_too_long_value(condition)
            elif condition_value.startswith("value<"):
                # Below minimum
                return self._generate_below_minimum_value(condition)
            elif condition_value.startswith("value>"):
                # Above maximum
                return self._generate_above_maximum_value(condition)
            else:
                # Use the value directly (e.g., enum value)
                return condition_value
        
        # Default: return as is
        return condition_value
    
    def _generate_valid_value(self, condition: DecisionCondition) -> Any:
        """Generate a valid value for a condition."""
        from src.shared.config import SwaggerConstants
        
        field_type = condition.constraint_details.get("expected_type", "string")
        
        # Use SwaggerConstants for valid values
        if field_type == "string":
            field_format = condition.constraint_details.get("format")
            if field_format == "uuid":
                return "550e8400-e29b-41d4-a716-446655440000"
            elif field_format == "email":
                return "user@example.com"
            elif field_format == "date":
                return "2023-01-01"
            else:
                return "valid_value"
        elif field_type == "integer":
            return 100
        elif field_type == "number":
            return 100.0
        elif field_type == "boolean":
            return True
        else:
            return "valid_value"
    
    def _generate_invalid_value(self, condition: DecisionCondition) -> Any:
        """Generate an invalid value for a condition."""
        field_type = condition.constraint_details.get("expected_type", "string")
        
        if field_type == "string":
            field_format = condition.constraint_details.get("format")
            if field_format == "uuid":
                return "invalid-uuid"
            elif field_format == "email":
                return "invalid-email"
            elif field_format == "date":
                return "not-a-date"
            else:
                return "!@#$%"
        elif field_type in ["integer", "number"]:
            return "not_a_number"
        elif field_type == "boolean":
            return "not_boolean"
        else:
            return None
    
    def _generate_too_short_value(self, condition: DecisionCondition) -> str:
        """Generate a value that is too short."""
        min_length = condition.constraint_details.get("min_length", 5)
        return "x" * max(0, min_length - 1)
    
    def _generate_too_long_value(self, condition: DecisionCondition) -> str:
        """Generate a value that is too long."""
        max_length = condition.constraint_details.get("max_length", 100)
        return "x" * (max_length + 1)
    
    def _generate_below_minimum_value(self, condition: DecisionCondition) -> float:
        """Generate a value below the minimum."""
        minimum = condition.constraint_details.get("minimum", 0)
        return minimum - 1
    
    def _generate_above_maximum_value(self, condition: DecisionCondition) -> float:
        """Generate a value above the maximum."""
        maximum = condition.constraint_details.get("maximum", 100)
        return maximum + 1
    
    def _find_executing_action(
        self,
        action_values: Dict[str, ActionValue],
        action_map: Dict[str, DecisionAction]
    ) -> DecisionAction:
        """Find the action that should execute (marked with X)."""
        for action_id, value in action_values.items():
            if value == ActionValue.EXECUTE:
                return action_map.get(action_id)
        
        # Default to first action
        return list(action_map.values())[0] if action_map else None
    
    def _generate_test_name(
        self,
        rule: DecisionRule,
        condition_map: Dict[str, DecisionCondition],
        expected_action: DecisionAction
    ) -> str:
        """Generate a descriptive test name."""
        # Count valid vs invalid conditions
        valid_count = 0
        invalid_count = 0
        
        for cond_id, value in rule.condition_values.items():
            if isinstance(value, ConditionValue):
                if value == ConditionValue.TRUE:
                    valid_count += 1
                elif value == ConditionValue.FALSE:
                    invalid_count += 1
            elif "invalid" in str(value).lower() or "<" in str(value) or ">" in str(value):
                invalid_count += 1
            else:
                valid_count += 1
        
        if invalid_count == 0:
            return f"All conditions valid - Expect {expected_action.expected_status_code}"
        else:
            return f"{invalid_count} invalid condition(s) - Expect {expected_action.expected_status_code}"
    
    def _generate_objective(
        self,
        rule: DecisionRule,
        condition_map: Dict[str, DecisionCondition],
        expected_action: DecisionAction
    ) -> str:
        """Generate test objective."""
        return f"Verify that {expected_action.description}"
    
    def _build_condition_summary(
        self,
        condition_values: Dict[str, Any],
        condition_map: Dict[str, DecisionCondition]
    ) -> Dict[str, Any]:
        """Build human-readable condition summary."""
        summary = {}
        for cond_id, value in condition_values.items():
            condition = condition_map.get(cond_id)
            if condition:
                summary[condition.field_name] = {
                    "condition_type": condition.condition_type.value,
                    "value": value.value if isinstance(value, ConditionValue) else value
                }
        return summary
    
    def _build_action_summary(
        self,
        action_values: Dict[str, ActionValue],
        action_map: Dict[str, DecisionAction]
    ) -> Dict[str, Any]:
        """Build human-readable action summary."""
        summary = {}
        for action_id, value in action_values.items():
            action = action_map.get(action_id)
            if action and value == ActionValue.EXECUTE:
                summary[str(action.expected_status_code)] = action.description
        return summary
    
    def _determine_priority(
        self,
        rule: DecisionRule,
        expected_action: DecisionAction
    ) -> str:
        """Determine test case priority."""
        if expected_action and expected_action.expected_status_code < 300:
            return TestPriorities.HIGH
        else:
            return TestPriorities.MEDIUM
    
    def _generate_tags(
        self,
        rule: DecisionRule,
        expected_action: DecisionAction
    ) -> List[str]:
        """Generate tags for the test case."""
        tags = ["decision_table"]
        
        if expected_action:
            if expected_action.expected_status_code < 300:
                tags.append("positive")
            else:
                tags.append("negative")
        
        return tags
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in IDs."""
        return name.replace("/", "_").replace("-", "_").replace(" ", "_")
