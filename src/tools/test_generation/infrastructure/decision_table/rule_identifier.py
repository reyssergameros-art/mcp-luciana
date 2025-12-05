"""
Rule Identifier for Decision Table technique (ISTQB v4).

This module identifies conditions and actions from Swagger analysis data.
Follows SOLID principles and DDD approach.

Responsibilities:
- Extract conditions from field constraints (headers, path params, body)
- Determine if condition is limited entry (boolean) or extended entry (multiple values)
- Extract actions from response definitions in Swagger
- Build domain models: DecisionCondition and DecisionAction
"""
from typing import Dict, Any, List, Optional
import logging

from ...domain.decision_table.models import (
    DecisionCondition,
    DecisionAction,
    ConditionType,
    ConditionValue
)
from ...domain.decision_table.exceptions import DecisionTableError
from src.shared.config import SwaggerConstants

logger = logging.getLogger(__name__)


class RuleIdentifier:
    """
    Identifies conditions and actions from Swagger analysis.
    
    Respects SOLID principles:
    - Single Responsibility: Only identifies conditions and actions
    - Open/Closed: Extensible for new condition types
    - Dependency Inversion: Returns domain models, not DTOs
    
    Dynamically determines:
    - Whether to use limited entry (boolean) or extended entry (multiple values)
    - Possible values for extended entry conditions
    - Expected actions based on response codes
    """
    
    def __init__(self):
        """Initialize rule identifier."""
        self.condition_counter = 0
        self.action_counter = 0
    
    def identify_conditions_and_actions(
        self,
        endpoint_data: Dict[str, Any]
    ) -> tuple[List[DecisionCondition], List[DecisionAction]]:
        """
        Identify all conditions and actions for an endpoint.
        
        Args:
            endpoint_data: Endpoint data from Swagger analysis
            
        Returns:
            Tuple of (conditions, actions)
            
        Raises:
            DecisionTableError: If identification fails
        """
        try:
            conditions = []
            actions = []
            
            endpoint = endpoint_data.get("path", "")
            method = endpoint_data.get("method", "")
            
            # Reset counters for this endpoint
            self.condition_counter = 0
            self.action_counter = 0
            
            # Identify conditions from headers
            for header in endpoint_data.get("headers", []):
                header_conditions = self._identify_conditions_from_field(
                    header, endpoint, method, "header"
                )
                conditions.extend(header_conditions)
            
            # Identify conditions from path parameters
            for path_param in endpoint_data.get("path_parameters", []):
                path_conditions = self._identify_conditions_from_field(
                    path_param, endpoint, method, "path"
                )
                conditions.extend(path_conditions)
            
            # Identify conditions from query parameters
            for query_param in endpoint_data.get("query_parameters", []):
                query_conditions = self._identify_conditions_from_field(
                    query_param, endpoint, method, "query"
                )
                conditions.extend(query_conditions)
            
            # Identify conditions from request body
            request_body = endpoint_data.get("request_body")
            if request_body and isinstance(request_body, dict):
                # Request body can be a dict of fields (Swagger analysis format)
                for field_name, field_data in request_body.items():
                    if isinstance(field_data, dict) and "data_type" in field_data:
                        body_conditions = self._identify_conditions_from_field(
                            field_data, endpoint, method, "body", field_name
                        )
                        conditions.extend(body_conditions)
            
            # Identify actions from responses
            responses = endpoint_data.get("responses", {})
            actions = self._identify_actions_from_responses(responses, endpoint, method)
            
            logger.debug(
                f"Identified {len(conditions)} conditions and {len(actions)} actions "
                f"for {method} {endpoint}"
            )
            
            return conditions, actions
            
        except Exception as e:
            raise DecisionTableError(
                f"Failed to identify conditions and actions: {str(e)}"
            ) from e
    
    def _identify_conditions_from_field(
        self,
        field_data: Dict[str, Any],
        endpoint: str,
        method: str,
        location: str,
        field_name: Optional[str] = None
    ) -> List[DecisionCondition]:
        """
        Identify conditions from a single field.
        
        Args:
            field_data: Field metadata with constraints
            endpoint: Endpoint path
            method: HTTP method
            location: Field location (header, path, query, body)
            field_name: Optional field name (for body fields)
            
        Returns:
            List of DecisionCondition objects
        """
        conditions = []
        
        if not field_name:
            field_name = field_data.get("name", "")
        
        if not field_name:
            return conditions
        
        field_type = field_data.get(SwaggerConstants.CONSTRAINT_TYPE, "string")
        
        # Required condition (boolean - limited entry)
        if field_data.get("required"):
            conditions.append(self._create_required_condition(
                field_name, location, endpoint, method
            ))
        
        # Format condition (can be limited or extended entry)
        field_format = field_data.get(SwaggerConstants.CONSTRAINT_FORMAT)
        if field_format and field_format != "none":
            conditions.append(self._create_format_condition(
                field_name, field_format, location, endpoint, method
            ))
        
        # Enum condition (extended entry)
        enum_values = field_data.get("enum_values")
        if enum_values:
            conditions.append(self._create_enum_condition(
                field_name, enum_values, location, endpoint, method, field_data
            ))
        
        # Length condition (extended entry)
        min_length = field_data.get("min_length")
        max_length = field_data.get("max_length")
        if min_length is not None or max_length is not None:
            conditions.append(self._create_length_condition(
                field_name, min_length, max_length, location, endpoint, method, field_data
            ))
        
        # Range condition (extended entry)
        minimum = field_data.get("minimum")
        maximum = field_data.get("maximum")
        if minimum is not None or maximum is not None:
            conditions.append(self._create_range_condition(
                field_name, minimum, maximum, location, endpoint, method, field_data
            ))
        
        # Type condition (limited entry - boolean)
        conditions.append(self._create_type_condition(
            field_name, field_type, location, endpoint, method
        ))
        
        return conditions
    
    def _create_required_condition(
        self,
        field_name: str,
        location: str,
        endpoint: str,
        method: str
    ) -> DecisionCondition:
        """Create a required field condition (limited entry)."""
        self.condition_counter += 1
        condition_id = f"C{self.condition_counter:03d}_{method}_{self._sanitize_name(field_name)}_required"
        
        return DecisionCondition(
            condition_id=condition_id,
            field_name=field_name,
            condition_type=ConditionType.REQUIRED,
            description=f"{field_name} is present",
            is_limited_entry=True,
            possible_values=[ConditionValue.TRUE, ConditionValue.FALSE],
            constraint_details={
                "location": location,
                "endpoint": endpoint,
                "method": method,
                "constraint": "required"
            }
        )
    
    def _create_format_condition(
        self,
        field_name: str,
        field_format: str,
        location: str,
        endpoint: str,
        method: str
    ) -> DecisionCondition:
        """Create a format validation condition (limited entry)."""
        self.condition_counter += 1
        condition_id = f"C{self.condition_counter:03d}_{method}_{self._sanitize_name(field_name)}_format"
        
        return DecisionCondition(
            condition_id=condition_id,
            field_name=field_name,
            condition_type=ConditionType.FORMAT,
            description=f"{field_name} has valid {field_format} format",
            is_limited_entry=True,
            possible_values=[ConditionValue.TRUE, ConditionValue.FALSE],
            constraint_details={
                "location": location,
                "endpoint": endpoint,
                "method": method,
                "constraint": "format",
                "format": field_format
            }
        )
    
    def _create_enum_condition(
        self,
        field_name: str,
        enum_values: List[Any],
        location: str,
        endpoint: str,
        method: str,
        field_data: Dict[str, Any]
    ) -> DecisionCondition:
        """Create an enum condition (extended entry)."""
        self.condition_counter += 1
        condition_id = f"C{self.condition_counter:03d}_{method}_{self._sanitize_name(field_name)}_enum"
        
        # Extended entry: multiple discrete values
        return DecisionCondition(
            condition_id=condition_id,
            field_name=field_name,
            condition_type=ConditionType.ENUM,
            description=f"{field_name} value",
            is_limited_entry=False,
            possible_values=enum_values + ["<invalid_value>"],  # Add invalid for testing
            constraint_details={
                "location": location,
                "endpoint": endpoint,
                "method": method,
                "constraint": "enum",
                "enum_values": enum_values
            }
        )
    
    def _create_length_condition(
        self,
        field_name: str,
        min_length: Optional[int],
        max_length: Optional[int],
        location: str,
        endpoint: str,
        method: str,
        field_data: Dict[str, Any]
    ) -> DecisionCondition:
        """Create a length condition (extended entry)."""
        self.condition_counter += 1
        condition_id = f"C{self.condition_counter:03d}_{method}_{self._sanitize_name(field_name)}_length"
        
        # Extended entry: valid, too short, too long
        possible_values = []
        if min_length is not None:
            possible_values.append(f"length<{min_length}")
        
        possible_values.append("valid_length")
        
        if max_length is not None:
            possible_values.append(f"length>{max_length}")
        
        return DecisionCondition(
            condition_id=condition_id,
            field_name=field_name,
            condition_type=ConditionType.LENGTH,
            description=f"{field_name} length",
            is_limited_entry=False,
            possible_values=possible_values,
            constraint_details={
                "location": location,
                "endpoint": endpoint,
                "method": method,
                "constraint": "length",
                "min_length": min_length,
                "max_length": max_length
            }
        )
    
    def _create_range_condition(
        self,
        field_name: str,
        minimum: Optional[float],
        maximum: Optional[float],
        location: str,
        endpoint: str,
        method: str,
        field_data: Dict[str, Any]
    ) -> DecisionCondition:
        """Create a range condition (extended entry)."""
        self.condition_counter += 1
        condition_id = f"C{self.condition_counter:03d}_{method}_{self._sanitize_name(field_name)}_range"
        
        # Extended entry: below minimum, valid, above maximum
        possible_values = []
        if minimum is not None:
            possible_values.append(f"value<{minimum}")
        
        possible_values.append("valid_range")
        
        if maximum is not None:
            possible_values.append(f"value>{maximum}")
        
        return DecisionCondition(
            condition_id=condition_id,
            field_name=field_name,
            condition_type=ConditionType.RANGE,
            description=f"{field_name} value range",
            is_limited_entry=False,
            possible_values=possible_values,
            constraint_details={
                "location": location,
                "endpoint": endpoint,
                "method": method,
                "constraint": "range",
                "minimum": minimum,
                "maximum": maximum
            }
        )
    
    def _create_type_condition(
        self,
        field_name: str,
        field_type: str,
        location: str,
        endpoint: str,
        method: str
    ) -> DecisionCondition:
        """Create a type validation condition (limited entry)."""
        self.condition_counter += 1
        condition_id = f"C{self.condition_counter:03d}_{method}_{self._sanitize_name(field_name)}_type"
        
        return DecisionCondition(
            condition_id=condition_id,
            field_name=field_name,
            condition_type=ConditionType.TYPE,
            description=f"{field_name} has correct type ({field_type})",
            is_limited_entry=True,
            possible_values=[ConditionValue.TRUE, ConditionValue.FALSE],
            constraint_details={
                "location": location,
                "endpoint": endpoint,
                "method": method,
                "constraint": "type",
                "expected_type": field_type
            }
        )
    
    def _identify_actions_from_responses(
        self,
        responses: Any,
        endpoint: str,
        method: str
    ) -> List[DecisionAction]:
        """
        Identify actions from response definitions.
        
        Args:
            responses: Response definitions from Swagger (list or dict)
            endpoint: Endpoint path
            method: HTTP method
            
        Returns:
            List of DecisionAction objects
        """
        actions = []
        
        # Handle both list and dict formats
        if isinstance(responses, list):
            # List format from Swagger analysis
            for response_data in responses:
                if not isinstance(response_data, dict):
                    continue
                    
                status_code = response_data.get("status_code")
                if not status_code:
                    continue
                
                try:
                    status_int = int(status_code)
                except ValueError:
                    logger.warning(f"Skipping non-numeric status code: {status_code}")
                    continue
                
                self.action_counter += 1
                action_id = f"A{self.action_counter:03d}_{method}_{status_code}"
                
                description = response_data.get("description", f"Response {status_code}")
                
                # Extract error code if it's an error response
                error_code = None
                if status_int >= 400:
                    error_code = response_data.get("error_code", f"ERR_{status_code}")
                
                action = DecisionAction(
                    action_id=action_id,
                    description=description,
                    expected_status_code=status_int,
                    expected_error=error_code,
                    metadata={
                        "endpoint": endpoint,
                        "method": method,
                        "response_data": response_data
                    }
                )
                
                actions.append(action)
        
        elif isinstance(responses, dict):
            # Dict format (legacy)
            for status_code, response_data in responses.items():
                try:
                    status_int = int(status_code)
                except ValueError:
                    logger.warning(f"Skipping non-numeric status code: {status_code}")
                    continue
                
                self.action_counter += 1
                action_id = f"A{self.action_counter:03d}_{method}_{status_code}"
                
                description = response_data.get("description", f"Response {status_code}")
                
                # Extract error code if it's an error response
                error_code = None
                if status_int >= 400:
                    error_code = response_data.get("error_code", f"ERR_{status_code}")
                
                action = DecisionAction(
                    action_id=action_id,
                    description=description,
                    expected_status_code=status_int,
                    expected_error=error_code,
                    metadata={
                        "endpoint": endpoint,
                        "method": method,
                        "response_data": response_data
                    }
                )
                
                actions.append(action)
        
        return actions
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize field name for use in IDs."""
        # Remove special characters and replace spaces with underscores
        return name.replace("-", "_").replace(" ", "_").replace("/", "_")
