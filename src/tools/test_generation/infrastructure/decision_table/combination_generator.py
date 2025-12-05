"""
Combination Generator for Decision Table technique (ISTQB v4).

Generates all feasible combinations of conditions for decision table rules.
Implements logic to detect infeasible combinations (N/A) and supports
table minimization by identifying irrelevant conditions.

According to ISTQB v4:
- A complete table covers every combination of conditions
- Infeasible combinations should be marked as N/A and excluded
- Tables can be minimized by merging columns with irrelevant conditions (–)
"""
from typing import List, Dict, Any, Optional
from itertools import product
import logging

from ...domain.decision_table.models import (
    DecisionCondition,
    DecisionRule,
    ConditionType,
    ConditionValue,
    ActionValue
)
from ...domain.decision_table.exceptions import InfeasibleCombinationError

logger = logging.getLogger(__name__)


class CombinationGenerator:
    """
    Generates all feasible combinations of conditions.
    
    Respects SOLID principles:
    - Single Responsibility: Only generates combinations
    - Open/Closed: Extensible for new infeasibility rules
    - Dependency Inversion: Works with domain models
    
    Handles:
    - Limited entry conditions (T/F)
    - Extended entry conditions (multiple values)
    - Detection of infeasible combinations
    - Generation of rule IDs
    """
    
    def __init__(self):
        """Initialize combination generator."""
        self.rule_counter = 0
    
    def generate_all_combinations(
        self,
        conditions: List[DecisionCondition],
        endpoint: str,
        method: str,
        minimize: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate all combinations of condition values.
        
        Args:
            conditions: List of conditions
            endpoint: Endpoint path
            method: HTTP method
            minimize: Whether to minimize the table (merge irrelevant conditions)
            
        Returns:
            List of combination dictionaries
        """
        if not conditions:
            logger.warning("No conditions provided for combination generation")
            return []
        
        # Reset counter
        self.rule_counter = 0
        
        # Build cartesian product of all possible values
        condition_ids = [c.condition_id for c in conditions]
        value_lists = [self._get_values_for_condition(c) for c in conditions]
        
        # Generate all combinations
        all_combinations = []
        for values in product(*value_lists):
            combination = dict(zip(condition_ids, values))
            
            # Check if combination is feasible
            if self._is_feasible(combination, conditions):
                self.rule_counter += 1
                rule_id = f"R{self.rule_counter:03d}_{method}_{self._sanitize_name(endpoint)}"
                
                combination_data = {
                    "rule_id": rule_id,
                    "condition_values": combination,
                    "is_feasible": True
                }
                all_combinations.append(combination_data)
            else:
                # Still track infeasible combinations for metrics
                self.rule_counter += 1
                rule_id = f"R{self.rule_counter:03d}_{method}_{self._sanitize_name(endpoint)}_NA"
                
                combination_data = {
                    "rule_id": rule_id,
                    "condition_values": combination,
                    "is_feasible": False
                }
                all_combinations.append(combination_data)
        
        logger.info(
            f"Generated {len(all_combinations)} combinations "
            f"({len([c for c in all_combinations if c['is_feasible']])} feasible) "
            f"for {method} {endpoint}"
        )
        
        # Apply minimization if requested
        if minimize:
            all_combinations = self._minimize_combinations(all_combinations, conditions)
        
        return all_combinations
    
    def _get_values_for_condition(self, condition: DecisionCondition) -> List[Any]:
        """
        Get all possible values for a condition.
        
        Args:
            condition: DecisionCondition object
            
        Returns:
            List of possible values
        """
        if condition.is_limited_entry:
            # Limited entry: T/F
            return [ConditionValue.TRUE, ConditionValue.FALSE]
        else:
            # Extended entry: use possible_values
            return condition.possible_values
    
    def _is_feasible(
        self,
        combination: Dict[str, Any],
        conditions: List[DecisionCondition]
    ) -> bool:
        """
        Determine if a combination of condition values is feasible.
        
        Infeasible combinations (N/A) include:
        1. Field not present (required=F) but other constraints are tested
        2. Invalid type but format/length/range constraints are tested
        3. Contradictory conditions
        
        Args:
            combination: Dictionary of condition_id -> value
            conditions: List of DecisionCondition objects
            
        Returns:
            True if feasible, False if infeasible (N/A)
        """
        # Build condition lookup
        condition_map = {c.condition_id: c for c in conditions}
        
        # Group conditions by field name
        field_conditions = {}
        for cond_id, value in combination.items():
            condition = condition_map.get(cond_id)
            if not condition:
                continue
            
            field_name = condition.field_name
            if field_name not in field_conditions:
                field_conditions[field_name] = {}
            
            field_conditions[field_name][condition.condition_type] = {
                "value": value,
                "condition_id": cond_id,
                "condition": condition
            }
        
        # Check infeasibility rules for each field
        for field_name, cond_types in field_conditions.items():
            # Rule 1: If field is not required (required=F) and not present,
            # other constraints are irrelevant/infeasible
            if ConditionType.REQUIRED in cond_types:
                required_value = cond_types[ConditionType.REQUIRED]["value"]
                if required_value == ConditionValue.FALSE:
                    # Field is not present - other constraints are infeasible
                    for cond_type, cond_data in cond_types.items():
                        if cond_type != ConditionType.REQUIRED:
                            # Testing constraints on absent field is infeasible
                            return False
            
            # Rule 2: If type is invalid (type=F), format/length/range are infeasible
            if ConditionType.TYPE in cond_types:
                type_value = cond_types[ConditionType.TYPE]["value"]
                if type_value == ConditionValue.FALSE:
                    # Invalid type - can't test format/length/range
                    constrained_types = [
                        ConditionType.FORMAT,
                        ConditionType.LENGTH,
                        ConditionType.RANGE,
                        ConditionType.ENUM
                    ]
                    for cond_type in constrained_types:
                        if cond_type in cond_types:
                            # Testing constraints on invalid type is infeasible
                            return False
            
            # Rule 3: If format is invalid (format=F), length/specific values are infeasible
            if ConditionType.FORMAT in cond_types:
                format_value = cond_types[ConditionType.FORMAT]["value"]
                if format_value == ConditionValue.FALSE:
                    # Invalid format - testing length on malformed data is infeasible
                    if ConditionType.LENGTH in cond_types:
                        length_value = cond_types[ConditionType.LENGTH]["value"]
                        # Only "valid_length" would be infeasible
                        if length_value == "valid_length":
                            return False
        
        return True
    
    def _minimize_combinations(
        self,
        combinations: List[Dict[str, Any]],
        conditions: List[DecisionCondition]
    ) -> List[Dict[str, Any]]:
        """
        Minimize the decision table by merging rules with irrelevant conditions.
        
        This is an optional optimization that reduces the number of test cases
        by identifying conditions that don't affect the outcome.
        
        Args:
            combinations: List of combination dictionaries
            conditions: List of DecisionCondition objects
            
        Returns:
            Minimized list of combinations
        """
        # TODO: Implement table minimization algorithm
        # This is a complex algorithm that merges rules where conditions
        # are irrelevant (marked with –) to the action outcome.
        # For now, return the original combinations.
        
        logger.info("Table minimization not yet implemented - returning full table")
        return combinations
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in IDs."""
        return name.replace("/", "_").replace("-", "_").replace(" ", "_")
