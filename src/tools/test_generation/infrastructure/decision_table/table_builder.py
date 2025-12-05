"""
Decision Table Builder for ISTQB v4 technique.

Constructs the complete decision table with ISTQB notation:
- Conditions: T (true), F (false), – (irrelevant), N/A (not feasible)
- Actions: X (execute), blank (don't execute)

Assembles conditions, actions, and rules into a complete DecisionTable.
"""
from typing import List, Dict, Any
import logging

from ...domain.decision_table.models import (
    DecisionTable,
    DecisionCondition,
    DecisionAction,
    DecisionRule,
    ActionValue
)
from ...domain.decision_table.exceptions import DecisionTableError

logger = logging.getLogger(__name__)


class DecisionTableBuilder:
    """
    Builds a complete decision table from components.
    
    Respects SOLID principles:
    - Single Responsibility: Only builds the table structure
    - Open/Closed: Extensible for new table features
    - Dependency Inversion: Works with domain models
    
    Responsibilities:
    - Combine conditions, actions, and combination data into DecisionRule objects
    - Assemble DecisionTable with proper ISTQB notation
    - Validate table structure
    """
    
    def build_table(
        self,
        endpoint: str,
        http_method: str,
        conditions: List[DecisionCondition],
        actions: List[DecisionAction],
        combinations: List[Dict[str, Any]],
        action_mappings: Dict[str, Dict[str, ActionValue]]
    ) -> DecisionTable:
        """
        Build a complete decision table.
        
        Args:
            endpoint: API endpoint path
            http_method: HTTP method
            conditions: List of all conditions
            actions: List of all actions
            combinations: List of combination data from CombinationGenerator
            action_mappings: Dictionary mapping rule_id -> (action_id -> ActionValue)
            
        Returns:
            Complete DecisionTable object
            
        Raises:
            DecisionTableError: If table construction fails
        """
        try:
            # Build DecisionRule objects
            rules = []
            for combination in combinations:
                rule_id = combination["rule_id"]
                condition_values = combination["condition_values"]
                is_feasible = combination["is_feasible"]
                
                # Get action values for this rule
                action_values = action_mappings.get(rule_id, {})
                
                # Only create rules for feasible combinations or if we want to track N/A
                if is_feasible or self._should_include_infeasible(combination):
                    rule = DecisionRule(
                        rule_id=rule_id,
                        condition_values=condition_values,
                        action_values=action_values,
                        is_feasible=is_feasible,
                        test_data={},  # Will be populated by TestCaseBuilder
                        priority="medium"
                    )
                    rules.append(rule)
            
            # Create decision table
            table = DecisionTable(
                endpoint=endpoint,
                http_method=http_method,
                conditions=conditions,
                actions=actions,
                rules=rules,
                is_minimized=False
            )
            
            logger.info(
                f"Built decision table for {http_method} {endpoint}: "
                f"{len(conditions)} conditions, {len(actions)} actions, "
                f"{len(rules)} rules ({len(table.get_feasible_rules())} feasible)"
            )
            
            return table
            
        except Exception as e:
            raise DecisionTableError(
                f"Failed to build decision table: {str(e)}"
            ) from e
    
    def _should_include_infeasible(self, combination: Dict[str, Any]) -> bool:
        """
        Determine if an infeasible combination should be included in the table.
        
        For documentation and metrics purposes, we may want to include
        infeasible combinations marked with N/A.
        
        Args:
            combination: Combination data
            
        Returns:
            True to include, False to exclude
        """
        # For now, include all combinations for completeness
        # In production, this could be configurable
        return False  # Exclude infeasible combinations from output
