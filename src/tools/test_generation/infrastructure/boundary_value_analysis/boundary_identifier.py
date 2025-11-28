"""
Dynamically identifies boundary values from Swagger field constraints.
Follows ISTQB v4 BVA definition for ordered partitions.
"""
from typing import List, Dict, Any
from ...domain.boundary_value_analysis.models import BoundaryValue, BoundaryType, BVAVersion


class BoundaryIdentifier:
    """Identifies boundary values from field constraints dynamically."""
    
    @staticmethod
    def identify_boundaries(
        field_name: str,
        field_type: str,
        constraints: Dict[str, Any],
        bva_version: BVAVersion = BVAVersion.TWO_VALUE
    ) -> List[BoundaryValue]:
        """
        Identify all boundary values for a field based on its constraints.
        Only applies to ordered partitions (strings with length, numbers with ranges, arrays with item counts).
        
        Args:
            field_name: Name of the field
            field_type: Type of the field
            constraints: Dictionary with constraints from swagger
            bva_version: BVA version (2-value or 3-value)
            
        Returns:
            List of BoundaryValue objects
        """
        boundaries = []
        
        # String boundaries (length constraints = ordered partition)
        if field_type in ["string", "str"]:
            boundaries.extend(
                BoundaryIdentifier._identify_string_boundaries(
                    field_name, constraints, bva_version
                )
            )
        
        # Numeric boundaries (value range = ordered partition)
        elif field_type in ["integer", "number", "int", "float", "int32", "int64"]:
            boundaries.extend(
                BoundaryIdentifier._identify_numeric_boundaries(
                    field_name, field_type, constraints, bva_version
                )
            )
        
        # Array boundaries (item count = ordered partition)
        elif field_type in ["array", "list"]:
            boundaries.extend(
                BoundaryIdentifier._identify_array_boundaries(
                    field_name, constraints, bva_version
                )
            )
        
        return boundaries
    
    @staticmethod
    def _identify_string_boundaries(
        field_name: str,
        constraints: Dict[str, Any],
        bva_version: BVAVersion
    ) -> List[BoundaryValue]:
        """Identify boundaries for string length constraints."""
        boundaries = []
        
        # minLength boundary
        min_length = constraints.get("min_length")
        if min_length is not None:
            min_length = int(min_length)
            
            # Boundary value: string with exact minLength
            boundary_val = "a" * min_length
            
            # Lower neighbor: minLength - 1 (invalid, too short)
            lower_val = "a" * (min_length - 1) if min_length > 0 else ""
            
            # Upper neighbor for 3-value: minLength + 1 (valid, within range)
            upper_val = "a" * (min_length + 1) if bva_version == BVAVersion.THREE_VALUE else None
            
            boundaries.append(BoundaryValue(
                field_name=field_name,
                field_type="string",
                boundary_type=BoundaryType.MINIMUM,
                boundary_value=boundary_val,
                lower_neighbor=lower_val,
                upper_neighbor=upper_val,
                constraint_type="minLength"
            ))
        
        # maxLength boundary
        max_length = constraints.get("max_length")
        if max_length is not None:
            max_length = int(max_length)
            
            # Boundary value: string with exact maxLength
            boundary_val = "a" * max_length
            
            # Lower neighbor for 3-value: maxLength - 1 (valid, within range)
            lower_val = "a" * (max_length - 1) if (bva_version == BVAVersion.THREE_VALUE and max_length > 0) else None
            
            # Upper neighbor: maxLength + 1 (invalid, too long)
            upper_val = "a" * (max_length + 1)
            
            boundaries.append(BoundaryValue(
                field_name=field_name,
                field_type="string",
                boundary_type=BoundaryType.MAXIMUM,
                boundary_value=boundary_val,
                lower_neighbor=lower_val,
                upper_neighbor=upper_val,
                constraint_type="maxLength"
            ))
        
        return boundaries
    
    @staticmethod
    def _identify_numeric_boundaries(
        field_name: str,
        field_type: str,
        constraints: Dict[str, Any],
        bva_version: BVAVersion
    ) -> List[BoundaryValue]:
        """Identify boundaries for numeric value constraints."""
        boundaries = []
        is_integer = field_type in ["integer", "int", "int32", "int64"]
        
        # minimum boundary
        minimum = constraints.get("minimum")
        if minimum is not None:
            if is_integer:
                boundary_val = int(minimum)
                lower_val = boundary_val - 1
                upper_val = boundary_val + 1 if bva_version == BVAVersion.THREE_VALUE else None
            else:
                boundary_val = float(minimum)
                lower_val = boundary_val - 0.1
                upper_val = boundary_val + 0.1 if bva_version == BVAVersion.THREE_VALUE else None
            
            boundaries.append(BoundaryValue(
                field_name=field_name,
                field_type=field_type,
                boundary_type=BoundaryType.MINIMUM,
                boundary_value=boundary_val,
                lower_neighbor=lower_val,
                upper_neighbor=upper_val,
                constraint_type="minimum"
            ))
        
        # maximum boundary
        maximum = constraints.get("maximum")
        if maximum is not None:
            if is_integer:
                boundary_val = int(maximum)
                lower_val = boundary_val - 1 if bva_version == BVAVersion.THREE_VALUE else None
                upper_val = boundary_val + 1
            else:
                boundary_val = float(maximum)
                lower_val = boundary_val - 0.1 if bva_version == BVAVersion.THREE_VALUE else None
                upper_val = boundary_val + 0.1
            
            boundaries.append(BoundaryValue(
                field_name=field_name,
                field_type=field_type,
                boundary_type=BoundaryType.MAXIMUM,
                boundary_value=boundary_val,
                lower_neighbor=lower_val,
                upper_neighbor=upper_val,
                constraint_type="maximum"
            ))
        
        return boundaries
    
    @staticmethod
    def _identify_array_boundaries(
        field_name: str,
        constraints: Dict[str, Any],
        bva_version: BVAVersion
    ) -> List[BoundaryValue]:
        """Identify boundaries for array items count constraints."""
        boundaries = []
        
        # minItems boundary
        min_items = constraints.get("min_items")
        if min_items is not None:
            min_items = int(min_items)
            
            boundaries.append(BoundaryValue(
                field_name=field_name,
                field_type="array",
                boundary_type=BoundaryType.MINIMUM,
                boundary_value=min_items,
                lower_neighbor=min_items - 1 if min_items > 0 else 0,
                upper_neighbor=min_items + 1 if bva_version == BVAVersion.THREE_VALUE else None,
                constraint_type="minItems"
            ))
        
        # maxItems boundary
        max_items = constraints.get("max_items")
        if max_items is not None:
            max_items = int(max_items)
            
            boundaries.append(BoundaryValue(
                field_name=field_name,
                field_type="array",
                boundary_type=BoundaryType.MAXIMUM,
                boundary_value=max_items,
                lower_neighbor=max_items - 1 if bva_version == BVAVersion.THREE_VALUE else None,
                upper_neighbor=max_items + 1,
                constraint_type="maxItems"
            ))
        
        return boundaries
