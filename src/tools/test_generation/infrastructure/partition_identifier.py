"""Service for identifying equivalence partitions from swagger constraints."""
from typing import Dict, Any, List, Optional
from uuid import UUID

from ..domain.models import (
    EquivalencePartition, PartitionType, PartitionCategory, PartitionSet
)
from ..domain.exceptions import PartitionIdentificationError
from src.shared.config import SwaggerConstants


class PartitionIdentifier:
    """
    Identifies equivalence partitions from swagger field constraints.
    
    Following ISTQB v4, this service divides data into partitions based on
    the expectation that all elements in a partition are processed the same way.
    
    Responsibilities (Single Responsibility Principle):
    - Analyze field constraints
    - Identify valid partitions
    - Identify invalid partitions
    - Generate partition IDs and descriptions
    """
    
    def __init__(self):
        self.partition_counter = 0
    
    def identify_partitions_for_field(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> PartitionSet:
        """
        Identify all equivalence partitions for a single field.
        
        Args:
            field_name: Name of the field
            field_data: Field metadata including constraints
            endpoint: Endpoint path (for context)
            
        Returns:
            PartitionSet with all identified partitions
            
        Raises:
            PartitionIdentificationError: If partitions cannot be identified
        """
        
        partitions: List[EquivalencePartition] = []
        field_type = field_data.get(SwaggerConstants.CONSTRAINT_TYPE, "string")
        
        try:
            # Identify partitions based on constraints present
            if field_data.get("min_length") or field_data.get("max_length"):
                partitions.extend(self._identify_length_partitions(field_name, field_data, endpoint))
            
            if field_data.get("minimum") is not None or field_data.get("maximum") is not None:
                partitions.extend(self._identify_range_partitions(field_name, field_data, endpoint))
            
            field_format = field_data.get(SwaggerConstants.CONSTRAINT_FORMAT, "none")
            if field_format != "none":
                partitions.extend(self._identify_format_partitions(field_name, field_data, endpoint))
            
            if field_data.get("enum_values"):
                partitions.extend(self._identify_enum_partitions(field_name, field_data, endpoint))
            
            if field_data.get("pattern"):
                partitions.extend(self._identify_pattern_partitions(field_name, field_data, endpoint))
            
            if field_data.get("required"):
                partitions.extend(self._identify_required_partitions(field_name, field_data, endpoint))
            
            # Always add type validation partitions
            partitions.extend(self._identify_type_partitions(field_name, field_data, endpoint))
            
            if not partitions:
                pass
            
            return PartitionSet(
                field_name=field_name,
                field_type=field_type,
                partitions=partitions
            )
            
        except Exception as e:
            raise PartitionIdentificationError(
                f"Failed to identify partitions for field '{field_name}': {str(e)}"
            )
    
    def _identify_length_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """Identify partitions for string length constraints."""
        partitions = []
        min_length = field_data.get("min_length")
        max_length = field_data.get("max_length")
        
        # Valid partition: within min and max
        if min_length is not None and max_length is not None:
            # Use middle value as representative
            mid_length = (min_length + max_length) // 2
            test_value = "a" * mid_length
            
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_length"),
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
                partition_id=self._generate_partition_id(endpoint, field_name, "below_min_length"),
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: length below minimum ({min_length})",
                test_value=test_value,
                constraint_details={
                    "min_length": min_length,
                    "test_length": below_min,
                    "expected_error": "RBV-003"
                },
                rationale=f"Tests invalid partition where length < {min_length}"
            ))
        
        # Invalid partition: above maximum
        if max_length is not None:
            above_max = max_length + SwaggerConstants.BOUNDARY_OFFSET_ABOVE
            test_value = "a" * above_max
            
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "above_max_length"),
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: length exceeds maximum ({max_length})",
                test_value=test_value,
                constraint_details={
                    "max_length": max_length,
                    "test_length": above_max,
                    "expected_error": "RBV-004"
                },
                rationale=f"Tests invalid partition where length > {max_length}"
            ))
        
        return partitions
    
    def _identify_range_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """Identify partitions for numeric range constraints."""
        partitions = []
        minimum = field_data.get("minimum")
        maximum = field_data.get("maximum")
        
        # Valid partition: within range
        if minimum is not None and maximum is not None:
            mid_value = (minimum + maximum) // 2
            
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_range"),
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
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_above_min"),
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
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_below_max"),
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
                partition_id=self._generate_partition_id(endpoint, field_name, "below_minimum"),
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
                partition_id=self._generate_partition_id(endpoint, field_name, "above_maximum"),
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
    
    def _identify_format_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """
        Identify partitions for format constraints.
        
        Supported OpenAPI/Swagger formats:
        - uuid: UUID v4 format (36 characters with hyphens)
        - email: Email address format
        - date/date-time: ISO 8601 date formats
        - uri/url: URI/URL format
        - ipv4: IPv4 address format (xxx.xxx.xxx.xxx)
        - ipv6: IPv6 address format
        - hostname: Valid hostname format
        
        Each format generates:
        - 1 valid partition with correct format example
        - N invalid partitions with malformed examples
        
        Args:
            field_name: Name of the field
            field_data: Field metadata from swagger analysis
            endpoint: Endpoint path for ID generation
            
        Returns:
            List of EquivalencePartition for format constraints
        """
        partitions = []
        field_format = field_data.get(SwaggerConstants.CONSTRAINT_FORMAT, "none")
        
        if field_format == "uuid":
            # Valid UUID partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_uuid"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description="Valid: correctly formatted UUID v4",
                test_value=SwaggerConstants.VALID_UUID_EXAMPLE,
                constraint_details={"format": "uuid"},
                rationale="Tests valid partition with correct UUID format"
            ))
            
            # Invalid UUID partitions - malformed format
            for idx, invalid_uuid in enumerate(SwaggerConstants.INVALID_UUID_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_uuid{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed UUID ({invalid_uuid or 'empty'})",
                    test_value=invalid_uuid,
                    constraint_details={
                        "format": "uuid",
                        "expected_error": "HDR-004"
                    },
                    rationale="Tests invalid partition with incorrect UUID format"
                ))
            
            # Invalid UUID partition - length too short
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "uuid_too_short"),
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: UUID length below {SwaggerConstants.UUID_LENGTH} chars",
                test_value=SwaggerConstants.UUID_TOO_SHORT_EXAMPLE,
                constraint_details={
                    "format": "uuid",
                    "expected_length": SwaggerConstants.UUID_LENGTH,
                    "actual_length": len(SwaggerConstants.UUID_TOO_SHORT_EXAMPLE),
                    "expected_error": "HDR-004"
                },
                rationale=f"Tests invalid partition where UUID length < {SwaggerConstants.UUID_LENGTH} characters"
            ))
            
            # Invalid UUID partition - length too long
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "uuid_too_long"),
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: UUID length exceeds {SwaggerConstants.UUID_LENGTH} chars",
                test_value=SwaggerConstants.UUID_TOO_LONG_EXAMPLE,
                constraint_details={
                    "format": "uuid",
                    "expected_length": SwaggerConstants.UUID_LENGTH,
                    "actual_length": len(SwaggerConstants.UUID_TOO_LONG_EXAMPLE),
                    "expected_error": "HDR-004"
                },
                rationale=f"Tests invalid partition where UUID length > {SwaggerConstants.UUID_LENGTH} characters"
            ))
        
        elif field_format == "email":
            # Valid email partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_email"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description="Valid: correctly formatted email",
                test_value=SwaggerConstants.VALID_EMAIL_EXAMPLE,
                constraint_details={"format": "email"},
                rationale="Tests valid partition with correct email format"
            ))
            
            # Invalid email partitions
            for idx, invalid_email in enumerate(SwaggerConstants.INVALID_EMAIL_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_email{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed email ({invalid_email or 'empty'})",
                    test_value=invalid_email,
                    constraint_details={"format": "email"},
                    rationale="Tests invalid partition with incorrect email format"
                ))
        
        elif field_format in ["date", "date-time"]:
            # Valid date partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_date"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Valid: correctly formatted {field_format}",
                test_value=SwaggerConstants.VALID_DATE_EXAMPLE,
                constraint_details={"format": field_format},
                rationale=f"Tests valid partition with correct {field_format} format"
            ))
            
            # Invalid date partitions
            for idx, invalid_date in enumerate(SwaggerConstants.INVALID_DATE_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_date{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed {field_format} ({invalid_date or 'empty'})",
                    test_value=invalid_date,
                    constraint_details={"format": field_format},
                    rationale=f"Tests invalid partition with incorrect {field_format} format"
                ))
        
        elif field_format in ["uri", "url"]:
            # Valid URI partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_uri"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Valid: correctly formatted {field_format}",
                test_value=SwaggerConstants.VALID_URI_EXAMPLE,
                constraint_details={"format": field_format},
                rationale=f"Tests valid partition with correct {field_format} format"
            ))
            
            # Invalid URI partitions
            for idx, invalid_uri in enumerate(SwaggerConstants.INVALID_URI_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_uri{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed {field_format} ({invalid_uri or 'empty'})",
                    test_value=invalid_uri,
                    constraint_details={"format": field_format},
                    rationale=f"Tests invalid partition with incorrect {field_format} format"
                ))
        
        elif field_format == "ipv4":
            # Valid IPv4 partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_ipv4"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description="Valid: correctly formatted IPv4 address",
                test_value=SwaggerConstants.VALID_IPV4_EXAMPLE,
                constraint_details={"format": "ipv4"},
                rationale="Tests valid partition with correct IPv4 format"
            ))
            
            # Invalid IPv4 partitions
            for idx, invalid_ip in enumerate(SwaggerConstants.INVALID_IPV4_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_ipv4{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed IPv4 address ({invalid_ip or 'empty'})",
                    test_value=invalid_ip,
                    constraint_details={"format": "ipv4"},
                    rationale="Tests invalid partition with incorrect IPv4 format"
                ))
        
        elif field_format == "ipv6":
            # Valid IPv6 partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_ipv6"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description="Valid: correctly formatted IPv6 address",
                test_value=SwaggerConstants.VALID_IPV6_EXAMPLE,
                constraint_details={"format": "ipv6"},
                rationale="Tests valid partition with correct IPv6 format"
            ))
            
            # Invalid IPv6 partitions
            for idx, invalid_ip in enumerate(SwaggerConstants.INVALID_IPV6_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_ipv6{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed IPv6 address ({invalid_ip or 'empty'})",
                    test_value=invalid_ip,
                    constraint_details={"format": "ipv6"},
                    rationale="Tests invalid partition with incorrect IPv6 format"
                ))
        
        elif field_format == "hostname":
            # Valid hostname partition
            partitions.append(EquivalencePartition(
                partition_id=self._generate_partition_id(endpoint, field_name, "valid_hostname"),
                partition_type=PartitionType.VALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description="Valid: correctly formatted hostname",
                test_value=SwaggerConstants.VALID_HOSTNAME_EXAMPLE,
                constraint_details={"format": "hostname"},
                rationale="Tests valid partition with correct hostname format"
            ))
            
            # Invalid hostname partitions
            for idx, invalid_host in enumerate(SwaggerConstants.INVALID_HOSTNAME_EXAMPLES):
                partitions.append(EquivalencePartition(
                    partition_id=self._generate_partition_id(endpoint, field_name, f"invalid_hostname{idx}"),
                    partition_type=PartitionType.INVALID,
                    category=PartitionCategory.FORMAT,
                    field_name=field_name,
                    description=f"Invalid: malformed hostname ({invalid_host or 'empty'})",
                    test_value=invalid_host,
                    constraint_details={"format": "hostname"},
                    rationale="Tests invalid partition with incorrect hostname format"
                ))
        
        return partitions
    
    def _identify_enum_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """Identify partitions for enum constraints."""
        partitions = []
        enum_values = field_data.get("enum_values", [])
        
        if not enum_values:
            return partitions
        
        # Valid partition: one representative from enum
        partitions.append(EquivalencePartition(
            partition_id=self._generate_partition_id(endpoint, field_name, "valid_enum"),
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
            partition_id=self._generate_partition_id(endpoint, field_name, "invalid_enum"),
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.ENUM,
            field_name=field_name,
            description=f"Invalid: value not in allowed enum",
            test_value=invalid_value,
            constraint_details={
                "enum_values": enum_values,
                "test_value": invalid_value
            },
            rationale=f"Tests invalid partition with value not in enum set"
        ))
        
        return partitions
    
    def _identify_pattern_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """Identify partitions for regex pattern constraints."""
        partitions = []
        pattern = field_data.get("pattern")
        
        if not pattern:
            return partitions
        
        # Note: Generating valid regex matches is complex and out of scope for now
        # This is a placeholder for future enhancement
        
        return partitions
    
    def _identify_required_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """Identify partitions for required field constraints."""
        partitions = []
        is_required = field_data.get("required", False)
        
        if not is_required:
            return partitions
        
        # Invalid partition: missing required field
        partitions.append(EquivalencePartition(
            partition_id=self._generate_partition_id(endpoint, field_name, "missing_required"),
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.REQUIRED,
            field_name=field_name,
            description="Invalid: required field is missing",
            test_value=None,
            constraint_details={
                "required": True,
                "expected_error": "RBV-001"
            },
            rationale="Tests invalid partition where required field is omitted"
        ))
        
        # Invalid partition: empty value for required field
        partitions.append(EquivalencePartition(
            partition_id=self._generate_partition_id(endpoint, field_name, "empty_required"),
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.REQUIRED,
            field_name=field_name,
            description="Invalid: required field is empty",
            test_value="",
            constraint_details={
                "required": True,
                "expected_error": "RBV-002"
            },
            rationale="Tests invalid partition where required field has empty value"
        ))
        
        return partitions
    
    def _identify_type_partitions(
        self,
        field_name: str,
        field_data: Dict[str, Any],
        endpoint: str
    ) -> List[EquivalencePartition]:
        """Identify partitions for data type constraints."""
        partitions = []
        field_type = field_data.get(SwaggerConstants.CONSTRAINT_TYPE, "string")
        
        # Invalid partition: wrong type
        invalid_type_value = "wrong_type_string" if field_type in ["integer", "number"] else 12345
        
        partitions.append(EquivalencePartition(
            partition_id=self._generate_partition_id(endpoint, field_name, "invalid_type"),
            partition_type=PartitionType.INVALID,
            category=PartitionCategory.TYPE,
            field_name=field_name,
            description=f"Invalid: wrong data type (expected {field_type})",
            test_value=invalid_type_value,
            constraint_details={
                "expected_type": field_type,
                "provided_type": type(invalid_type_value).__name__
            },
            rationale=f"Tests invalid partition with incorrect data type"
        ))
        
        return partitions
    
    def _generate_partition_id(self, endpoint: str, field_name: str, partition_type: str) -> str:
        """Generate unique partition ID."""
        self.partition_counter += 1
        # Sanitize endpoint for ID
        endpoint_safe = endpoint.replace("/", "").replace("{", "").replace("}", "").strip("")
        return f"{SwaggerConstants.TEST_ID_PREFIX_EP}{endpoint_safe}{field_name}{partition_type}{self.partition_counter}"