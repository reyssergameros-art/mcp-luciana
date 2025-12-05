"""
Action Resolver for Decision Table technique (ISTQB v4).

Determines which actions should occur (X) or not occur (blank) for each
combination of conditions. Reuses existing status code and error code
resolvers from Equivalence Partitioning technique.

According to ISTQB v4:
- Actions marked with X should occur
- Actions left blank should not occur
- Only one action typically occurs per rule (one response code)
"""
from typing import Dict, Any, List
import logging

from ...domain.decision_table.models import (
    DecisionAction,
    DecisionCondition,
    ConditionType,
    ConditionValue,
    ActionValue
)
from ...domain.decision_table.exceptions import DecisionTableError

# Reuse existing resolvers from EP technique
from ...infrastructure.equivalence_partitioning.status_code_resolver import StatusCodeResolver
from ...infrastructure.equivalence_partitioning.error_code_resolver import ErrorCodeResolver

logger = logging.getLogger(__name__)


class DecisionTableActionResolver:
    """
    Resolves which actions should execute for each combination of conditions.
    
    Respects SOLID principles:
    - Single Responsibility: Only resolves actions
    - Dependency Inversion: Reuses existing resolvers
    - Open/Closed: Extensible for new action resolution logic
    
    Logic:
    - If all conditions are valid (T or valid values), expect success (2xx)
    - If any condition is invalid (F or invalid values), expect error (4xx)
    - Prioritize specific errors based on condition type
    """
    
    def __init__(self):
        """Initialize action resolver with reusable resolvers."""
        self.status_resolver = StatusCodeResolver()
        self.error_resolver = ErrorCodeResolver()
    
    def resolve_actions(
        self,
        combination: Dict[str, Any],
        conditions: List[DecisionCondition],
        actions: List[DecisionAction]
    ) -> Dict[str, ActionValue]:
        """
        Determine which actions should execute for a combination.
        
        Args:
            combination: Dictionary of condition_id -> value
            conditions: List of all conditions
            actions: List of all possible actions
            
        Returns:
            Dictionary of action_id -> ActionValue (X or blank)
        """
        # Build condition lookup
        condition_map = {c.condition_id: c for c in conditions}
        
        # Analyze combination to determine expected outcome
        all_valid = True
        has_invalid = False
        invalid_types = []
        
        for cond_id, value in combination.items():
            condition = condition_map.get(cond_id)
            if not condition:
                continue
            
            # Check if this condition is invalid
            if condition.is_limited_entry:
                if value == ConditionValue.FALSE:
                    all_valid = False
                    has_invalid = True
                    invalid_types.append(condition.condition_type)
            else:
                # Extended entry: check for invalid values
                if self._is_invalid_value(value, condition):
                    all_valid = False
                    has_invalid = True
                    invalid_types.append(condition.condition_type)
        
        # Determine expected status code
        expected_status = self._determine_expected_status(
            all_valid, invalid_types, actions
        )
        
        # Build action values dictionary
        action_values = {}
        for action in actions:
            if action.expected_status_code == expected_status:
                action_values[action.action_id] = ActionValue.EXECUTE
            else:
                action_values[action.action_id] = ActionValue.NO_EXECUTE
        
        return action_values
    
    def _is_invalid_value(self, value: Any, condition: DecisionCondition) -> bool:
        """
        Check if a value is invalid for an extended entry condition.
        
        Args:
            value: The value to check
            condition: The condition definition
            
        Returns:
            True if invalid, False if valid
        """
        if isinstance(value, ConditionValue):
            return value == ConditionValue.FALSE
        
        # Check for invalid markers in extended entry
        if isinstance(value, str):
            invalid_markers = [
                "<invalid",
                "length<",
                "length>",
                "value<",
                "value>"
            ]
            return any(marker in value for marker in invalid_markers)
        
        return False
    
    def _determine_expected_status(
        self,
        all_valid: bool,
        invalid_types: List[ConditionType],
        actions: List[DecisionAction]
    ) -> int:
        """
        Determine expected status code based on condition validity.
        
        Args:
            all_valid: Whether all conditions are valid
            invalid_types: List of condition types that are invalid
            actions: List of available actions
            
        Returns:
            Expected HTTP status code
        """
        if all_valid:
            # All conditions valid - expect success
            # Find 2xx status code
            success_codes = [200, 201, 202, 204]
            for action in actions:
                if action.expected_status_code in success_codes:
                    return action.expected_status_code
            
            # Fallback to first 2xx code
            for action in actions:
                if 200 <= action.expected_status_code < 300:
                    return action.expected_status_code
            
            # If no success code defined, default to 200
            return 200
        
        else:
            # Some conditions invalid - expect error
            # Prioritize error codes based on condition type
            
            # Required field missing -> 400
            if ConditionType.REQUIRED in invalid_types:
                return self._find_status_code(actions, [400, 422])
            
            # Type invalid -> 400
            if ConditionType.TYPE in invalid_types:
                return self._find_status_code(actions, [400, 422])
            
            # Format invalid -> 400 or 422
            if ConditionType.FORMAT in invalid_types:
                return self._find_status_code(actions, [400, 422])
            
            # Length/Range invalid -> 400 or 422
            if ConditionType.LENGTH in invalid_types or ConditionType.RANGE in invalid_types:
                return self._find_status_code(actions, [400, 422])
            
            # Enum invalid -> 400
            if ConditionType.ENUM in invalid_types:
                return self._find_status_code(actions, [400, 422])
            
            # Default to 400
            return self._find_status_code(actions, [400, 422, 500])
    
    def _find_status_code(self, actions: List[DecisionAction], preferred_codes: List[int]) -> int:
        """
        Find a status code from list of preferred codes.
        
        Args:
            actions: List of available actions
            preferred_codes: List of preferred status codes in priority order
            
        Returns:
            First matching status code, or first preferred code if none match
        """
        action_codes = {action.expected_status_code for action in actions}
        
        for code in preferred_codes:
            if code in action_codes:
                return code
        
        # Fallback to first preferred code
        return preferred_codes[0] if preferred_codes else 400
