"""Refactored partition identifier using SOLID principles and specialized generators."""
from typing import Dict, Any, List

from ...domain.equivalence_partitioning.models import PartitionSet
from ...domain.equivalence_partitioning.exceptions import PartitionIdentificationError
from .format_partition_factory import FormatPartitionGeneratorFactory
from .constraint_partition_generators import (
    LengthPartitionGenerator,
    RangePartitionGenerator,
    EnumPartitionGenerator,
    RequiredPartitionGenerator,
    TypePartitionGenerator
)
from src.shared.config import SwaggerConstants


class PartitionIdentifierRefactored:
    """
    Refactored partition identifier following SOLID principles.
    
    Improvements:
    - Single Responsibility: Uses specialized generators for each constraint type
    - Open/Closed: Easy to add new constraint types without modifying this class
    - Dependency Inversion: Depends on abstractions (generators) not implementations
    - No hardcoded data: All test values come from SwaggerConstants or generators
    
    This class orchestrates partition generation by delegating to specialized generators.
    """
    
    def __init__(self):
        """Initialize partition identifier with specialized generators."""
        self.partition_counter = 0
        
        # Initialize constraint generators
        self.length_generator = LengthPartitionGenerator()
        self.range_generator = RangePartitionGenerator()
        self.enum_generator = EnumPartitionGenerator()
        self.required_generator = RequiredPartitionGenerator()
        self.type_generator = TypePartitionGenerator()
    
    def identify_partitions_for_field(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> PartitionSet:
        """
        Identify all equivalence partitions for a single field.
        
        Delegates to specialized generators based on constraint types present.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata including constraints
            endpoint: Endpoint path (for context)
            
        Returns:
            PartitionSet with all identified partitions
            
        Raises:
            PartitionIdentificationError: If partitions cannot be identified
        """
        partitions = []
        field_type = field_data.get(SwaggerConstants.CONSTRAINT_TYPE, "string")
        partition_id_base = self._generate_partition_id_base(endpoint, field_name)
        
        try:
            # Generate partitions based on constraints present
            
            # Length constraints
            if field_data.get("min_length") or field_data.get("max_length"):
                partitions.extend(
                    self.length_generator.generate_partitions(
                        field_name, field_data, partition_id_base
                    )
                )
            
            # Range constraints
            if field_data.get("minimum") is not None or field_data.get("maximum") is not None:
                partitions.extend(
                    self.range_generator.generate_partitions(
                        field_name, field_data, partition_id_base
                    )
                )
            
            # Format constraints
            field_format = field_data.get(SwaggerConstants.CONSTRAINT_FORMAT, "none")
            if field_format != "none":
                partitions.extend(
                    self._generate_format_partitions(
                        field_name, field_format, partition_id_base
                    )
                )
            
            # Enum constraints
            if field_data.get("enum_values"):
                partitions.extend(
                    self.enum_generator.generate_partitions(
                        field_name, field_data, partition_id_base
                    )
                )
            
            # Required field constraints
            if field_data.get("required"):
                partitions.extend(
                    self.required_generator.generate_partitions(
                        field_name, field_data, partition_id_base
                    )
                )
            
            # Type constraints (always add)
            partitions.extend(
                self.type_generator.generate_partitions(
                    field_name, field_data, partition_id_base
                )
            )
            
            return PartitionSet(
                field_name=field_name,
                field_type=field_type,
                partitions=partitions
            )
            
        except Exception as e:
            raise PartitionIdentificationError(
                f"Failed to identify partitions for field '{field_name}': {str(e)}"
            )
    
    def _generate_format_partitions(
        self,
        field_name: str,
        field_format: str,
        partition_id_base: str
    ) -> List:
        """
        Generate format partitions using factory pattern.
        
        Args:
            field_name: Name of the field
            field_format: Format type (uuid, email, etc.)
            partition_id_base: Base for partition IDs
            
        Returns:
            List of EquivalencePartition objects
        """
        partitions = []
        
        try:
            # Use factory to get appropriate generator
            generator = FormatPartitionGeneratorFactory.create_generator(field_format)
            
            # Generate valid partition
            valid_partition = generator.generate_valid_partition(
                field_name, partition_id_base
            )
            partitions.append(valid_partition)
            
            # Generate invalid partitions
            invalid_partitions = generator.generate_invalid_partitions(
                field_name, partition_id_base
            )
            partitions.extend(invalid_partitions)
            
        except ValueError as e:
            # Format not supported, skip format partitions
            pass
        
        return partitions
    
    def _generate_partition_id_base(self, endpoint: str, field_name: str) -> str:
        """
        Generate base string for partition IDs.
        
        Args:
            endpoint: Endpoint path
            field_name: Field name
            
        Returns:
            Base ID string
        """
        self.partition_counter += 1
        # Sanitize endpoint for ID
        endpoint_safe = endpoint.replace("/", "").replace("{", "").replace("}", "").strip()
        return f"{SwaggerConstants.TEST_ID_PREFIX_EP}{endpoint_safe}{field_name}"
