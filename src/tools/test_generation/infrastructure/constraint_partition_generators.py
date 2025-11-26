"""Generators for constraint-specific partitions (length, range, required, etc.)."""
from typing import List, Dict, Any

from ..domain.models import EquivalencePartition, PartitionType, PartitionCategory
from src.shared.config import SwaggerConstants


class LengthPartitionGenerator:
    """
    Generates partitions for string length constraints.
    
    Follows Single Responsibility Principle - only handles length partitions.
    """
    
    def generate_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """
        Generate valid and invalid partitions for length constraints.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata with min_length/max_length
            partition_id_base: Base string for partition IDs
            
        Returns:
            List of EquivalencePartition objects
        """
        partitions = []
        min_length = field_data.get("min_length")
        max_length = field_data.get("max_length")
        
        # Valid partition: within min and max
        if min_length is not None and max_length is not None:
            mid_length = (min_length + max_length) // 2
            test_value = "a" * mid_length
            
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}valid_length",
                partition_type=PartitionType.VALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Valid: length between {min_length} and {max_length} characters",
                test_value=test_value,
                constraint_details={
                    "min_length": min_length,
                    "max_length": max_length,
                    "test_length": mid_length
                },
                rationale=f"Tests valid partition where length satisfies {min_length} ≤ length ≤ {max_length}"
            ))
        
        # Invalid partition: below minimum
        if min_length is not None and min_length > 0:
            below_min = max(0, min_length - SwaggerConstants.BOUNDARY_OFFSET_BELOW)
            test_value = "a" * below_min
            
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}length_below_min",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: length below minimum ({below_min} < {min_length})",
                test_value=test_value,
                constraint_details={
                    "min_length": min_length,
                    "test_length": below_min
                },
                rationale=f"Tests invalid partition where length < {min_length}"
            ))
        
        # Invalid partition: above maximum
        if max_length is not None:
            above_max = max_length + SwaggerConstants.BOUNDARY_OFFSET_ABOVE
            test_value = "a" * above_max
            
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}length_above_max",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: length exceeds maximum ({above_max} > {max_length})",
                test_value=test_value,
                constraint_details={
                    "max_length": max_length,
                    "test_length": above_max
                },
                rationale=f"Tests invalid partition where length > {max_length}"
            ))
        
        return partitions


class RangePartitionGenerator:
    """
    Generates partitions for numeric range constraints.
    
    Follows Single Responsibility Principle - only handles range partitions.
    """
    
    def generate_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """
        Generate valid and invalid partitions for range constraints.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata with minimum/maximum
            partition_id_base: Base string for partition IDs
            
        Returns:
            List of EquivalencePartition objects
        """
        partitions = []
        minimum = field_data.get("minimum")
        maximum = field_data.get("maximum")
        
        # Valid partition: within range
        if minimum is not None and maximum is not None:
            mid_value = (minimum + maximum) // 2
            
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}valid_range",
                partition_type=PartitionType.VALID,
                category=PartitionCategory.RANGE,
                field_name=field_name,
                description=f"Valid: value between {minimum} and {maximum}",
                test_value=mid_value,
                constraint_details={
                    "minimum": minimum,
                    "maximum": maximum,
                    "test_value": mid_value
                },
                rationale=f"Tests valid partition where {minimum} ≤ value ≤ {maximum}"
            ))
        elif minimum is not None:
            test_value = minimum + 10
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}valid_above_min",
                partition_type=PartitionType.VALID,
                category=PartitionCategory.RANGE,
                field_name=field_name,
                description=f"Valid: value above minimum ({minimum})",
                test_value=test_value,
                constraint_details={"minimum": minimum, "test_value": test_value},
                rationale=f"Tests valid partition where value ≥ {minimum}"
            ))
        elif maximum is not None:
            test_value = maximum - 10
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}valid_below_max",
                partition_type=PartitionType.VALID,
                category=PartitionCategory.RANGE,
                field_name=field_name,
                description=f"Valid: value below maximum ({maximum})",
                test_value=test_value,
                constraint_details={"maximum": maximum, "test_value": test_value},
                rationale=f"Tests valid partition where value ≤ {maximum}"
            ))
        
        # Invalid partition: below minimum
        if minimum is not None:
            below_min = minimum - SwaggerConstants.BOUNDARY_OFFSET_BELOW
            
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}below_minimum",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.RANGE,
                field_name=field_name,
                description=f"Invalid: value below minimum ({minimum})",
                test_value=below_min,
                constraint_details={
                    "minimum": minimum,
                    "test_value": below_min
                },
                rationale=f"Tests invalid partition where value < {minimum}"
            ))
        
        # Invalid partition: above maximum
        if maximum is not None:
            above_max = maximum + SwaggerConstants.BOUNDARY_OFFSET_ABOVE
            
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}above_maximum",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.RANGE,
                field_name=field_name,
                description=f"Invalid: value exceeds maximum ({maximum})",
                test_value=above_max,
                constraint_details={
                    "maximum": maximum,
                    "test_value": above_max
                },
                rationale=f"Tests invalid partition where value > {maximum}"
            ))
        
        return partitions


class EnumPartitionGenerator:
    """
    Generates partitions for enum constraints.
    
    Follows Single Responsibility Principle - only handles enum partitions.
    """
    
    def generate_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """
        Generate valid and invalid partitions for enum constraints.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata with enum_values
            partition_id_base: Base string for partition IDs
            
        Returns:
            List of EquivalencePartition objects
        """
        partitions = []
        enum_values = field_data.get("enum_values", [])
        
        if not enum_values:
            return partitions
        
        # Valid partition: one representative from enum
        partitions.append(EquivalencePartition(
            partition_id=f"{partition_id_base}valid_enum",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.ENUM,
            field_name=field_name,
            description=f"Valid: value from allowed enum ({enum_values[0]})",
            test_value=enum_values[0],
            constraint_details={"enum_values": enum_values},
            rationale=f"Tests valid partition with value from enum set {enum_values}"
        ))
        
        # Invalid partition: value not in enum
        invalid_value = "INVALID_ENUM_VALUE"
        partitions.append(EquivalencePartition(
            partition_id=f"{partition_id_base}invalid_enum",
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.ENUM,
            field_name=field_name,
            description="Invalid: value not in allowed enum",
            test_value=invalid_value,
            constraint_details={
                "enum_values": enum_values,
                "test_value": invalid_value
            },
            rationale="Tests invalid partition with value not in enum set"
        ))
        
        return partitions


class RequiredPartitionGenerator:
    """
    Generates partitions for required field constraints.
    
    Follows Single Responsibility Principle - only handles required partitions.
    """
    
    def generate_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """
        Generate invalid partitions for required field constraints.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata with required flag
            partition_id_base: Base string for partition IDs
            
        Returns:
            List of EquivalencePartition objects
        """
        partitions = []
        is_required = field_data.get("required", False)
        
        if not is_required:
            return partitions
        
        # Invalid partition: missing required field
        partitions.append(EquivalencePartition(
            partition_id=f"{partition_id_base}missing_required",
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.REQUIRED,
            field_name=field_name,
            description="Invalid: required field is missing",
            test_value=None,
            constraint_details={
                "required": True
            },
            rationale="Tests invalid partition where required field is omitted"
        ))
        
        # Invalid partition: empty value for required field
        partitions.append(EquivalencePartition(
            partition_id=f"{partition_id_base}empty_required",
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.REQUIRED,
            field_name=field_name,
            description="Invalid: required field is empty",
            test_value="",
            constraint_details={
                "required": True
            },
            rationale="Tests invalid partition where required field has empty value"
        ))
        
        return partitions


class TypePartitionGenerator:
    """
    Generates partitions for data type constraints.
    
    Follows Single Responsibility Principle - only handles type partitions.
    """
    
    def generate_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """
        Generate invalid partitions for data type constraints.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata with type information
            partition_id_base: Base string for partition IDs
            
        Returns:
            List of EquivalencePartition objects
        """
        partitions = []
        field_type = field_data.get(SwaggerConstants.CONSTRAINT_TYPE, "string")
        
        # Invalid partition: wrong type
        if field_type in ["integer", "number"]:
            invalid_type_value = "wrong_type_string"
        else:
            invalid_type_value = 12345
        
        partitions.append(EquivalencePartition(
            partition_id=f"{partition_id_base}invalid_type",
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.TYPE,
            field_name=field_name,
            description=f"Invalid: wrong data type (expected {field_type})",
            test_value=invalid_type_value,
            constraint_details={
                "expected_type": field_type,
                "provided_type": type(invalid_type_value).__name__
            },
            rationale="Tests invalid partition with incorrect data type"
        ))
        
        return partitions
