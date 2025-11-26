"""Builder for creating validation constraints from schema definitions."""
from typing import List, Dict, Any, Union

from ..domain.models import ValidationConstraint
from ....shared.config import SwaggerConstants


class ConstraintsBuilder:
    """
    Responsible for building ValidationConstraint objects from schema definitions.
    
    Follows Single Responsibility Principle and DRY - eliminates duplicate constraint extraction code.
    """
    
    def __init__(self):
        """Initialize constraints builder."""
        pass
    
    def build_from_schema(self, schema: Dict[str, Any]) -> List[ValidationConstraint]:
        """
        Build list of ValidationConstraint objects from a schema definition.
        
        Args:
            schema: Schema dictionary containing validation rules
            
        Returns:
            List of ValidationConstraint objects
        """
        if not isinstance(schema, dict):
            return []
        
        constraints = []
        
        # Min length constraint
        if SwaggerConstants.CONSTRAINT_MIN_LENGTH in schema:
            constraint = self._build_min_length_constraint(
                schema[SwaggerConstants.CONSTRAINT_MIN_LENGTH]
            )
            constraints.append(constraint)
        
        # Max length constraint
        if SwaggerConstants.CONSTRAINT_MAX_LENGTH in schema:
            constraint = self._build_max_length_constraint(
                schema[SwaggerConstants.CONSTRAINT_MAX_LENGTH]
            )
            constraints.append(constraint)
        
        # Pattern constraint
        if SwaggerConstants.CONSTRAINT_PATTERN in schema:
            constraint = self._build_pattern_constraint(
                schema[SwaggerConstants.CONSTRAINT_PATTERN]
            )
            constraints.append(constraint)
        
        # Enum constraint
        if SwaggerConstants.CONSTRAINT_ENUM in schema:
            constraint = self._build_enum_constraint(
                schema[SwaggerConstants.CONSTRAINT_ENUM]
            )
            constraints.append(constraint)
        
        # Minimum value constraint
        if SwaggerConstants.CONSTRAINT_MINIMUM in schema:
            constraint = self._build_minimum_constraint(
                schema[SwaggerConstants.CONSTRAINT_MINIMUM]
            )
            constraints.append(constraint)
        
        # Maximum value constraint
        if SwaggerConstants.CONSTRAINT_MAXIMUM in schema:
            constraint = self._build_maximum_constraint(
                schema[SwaggerConstants.CONSTRAINT_MAXIMUM]
            )
            constraints.append(constraint)
        
        return constraints
    
    def _build_min_length_constraint(self, value: int) -> ValidationConstraint:
        """Build minimum length constraint."""
        return ValidationConstraint(
            constraint_type=SwaggerConstants.CONSTRAINT_TYPE_MIN_LENGTH,
            value=value,
            error_code=None,
            error_message=f"Minimum length is {value} characters"
        )
    
    def _build_max_length_constraint(self, value: int) -> ValidationConstraint:
        """Build maximum length constraint."""
        return ValidationConstraint(
            constraint_type=SwaggerConstants.CONSTRAINT_TYPE_MAX_LENGTH,
            value=value,
            error_code=None,
            error_message=f"Maximum length is {value} characters"
        )
    
    def _build_pattern_constraint(self, value: str) -> ValidationConstraint:
        """Build pattern constraint."""
        return ValidationConstraint(
            constraint_type=SwaggerConstants.CONSTRAINT_TYPE_PATTERN,
            value=value,
            error_code=None,
            error_message=f"Must match pattern: {value}"
        )
    
    def _build_enum_constraint(self, value: List[Any]) -> ValidationConstraint:
        """Build enum constraint."""
        values_str = ', '.join(map(str, value))
        return ValidationConstraint(
            constraint_type=SwaggerConstants.CONSTRAINT_TYPE_ENUM,
            value=value,
            error_code=None,
            error_message=f"Must be one of: {values_str}"
        )
    
    def _build_minimum_constraint(self, value: Union[int, float]) -> ValidationConstraint:
        """Build minimum value constraint."""
        return ValidationConstraint(
            constraint_type=SwaggerConstants.CONSTRAINT_TYPE_MINIMUM,
            value=value,
            error_code=None,
            error_message=f"Minimum value is {value}"
        )
    
    def _build_maximum_constraint(self, value: Union[int, float]) -> ValidationConstraint:
        """Build maximum value constraint."""
        return ValidationConstraint(
            constraint_type=SwaggerConstants.CONSTRAINT_TYPE_MAXIMUM,
            value=value,
            error_code=None,
            error_message=f"Maximum value is {value}"
        )
    
    def get_field_metadata(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract field metadata from schema (without building constraints).
        
        Returns basic field information like enum_values, pattern, min/max values.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            Dictionary with metadata fields
        """
        return {
            'enum_values': schema.get(SwaggerConstants.CONSTRAINT_ENUM),
            'pattern': schema.get(SwaggerConstants.CONSTRAINT_PATTERN),
            'minimum': schema.get(SwaggerConstants.CONSTRAINT_MINIMUM),
            'maximum': schema.get(SwaggerConstants.CONSTRAINT_MAXIMUM),
            'min_length': schema.get(SwaggerConstants.CONSTRAINT_MIN_LENGTH),
            'max_length': schema.get(SwaggerConstants.CONSTRAINT_MAX_LENGTH)
        }