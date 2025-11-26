"""Factory for creating format-specific partition generators."""
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from ..domain.models import EquivalencePartition, PartitionType, PartitionCategory
from src.shared.config import SwaggerConstants


class FormatPartitionGenerator(ABC):
    """
    Abstract base class for format-specific partition generators.
    
    Follows Open/Closed Principle - open for extension, closed for modification.
    Each format type has its own generator class.
    """
    
    @abstractmethod
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid partition for this format."""
        pass
    
    @abstractmethod
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid partitions for this format."""
        pass


class UUIDPartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for UUID format validation."""
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid UUID partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_uuid",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description="Valid: correctly formatted UUID v4",
            test_value=SwaggerConstants.VALID_UUID_EXAMPLE,
            constraint_details={"format": "uuid"},
            rationale="Tests valid partition with correct UUID format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid UUID partitions."""
        partitions = []
        
        # Malformed UUIDs
        for idx, invalid_uuid in enumerate(SwaggerConstants.INVALID_UUID_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_uuid{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed UUID ({invalid_uuid or 'empty'})",
                test_value=invalid_uuid,
                constraint_details={
                    "format": "uuid"
                },
                rationale="Tests invalid partition with incorrect UUID format"
            ))
        
        # Length violations
        partitions.extend([
            EquivalencePartition(
                partition_id=f"{partition_id_base}uuid_too_short",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: UUID length below {SwaggerConstants.UUID_LENGTH} chars",
                test_value=SwaggerConstants.UUID_TOO_SHORT_EXAMPLE,
                constraint_details={
                    "format": "uuid",
                    "expected_length": SwaggerConstants.UUID_LENGTH,
                    "actual_length": len(SwaggerConstants.UUID_TOO_SHORT_EXAMPLE)
                },
                rationale=f"Tests invalid partition where UUID length < {SwaggerConstants.UUID_LENGTH} characters"
            ),
            EquivalencePartition(
                partition_id=f"{partition_id_base}uuid_too_long",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.LENGTH,
                field_name=field_name,
                description=f"Invalid: UUID length exceeds {SwaggerConstants.UUID_LENGTH} chars",
                test_value=SwaggerConstants.UUID_TOO_LONG_EXAMPLE,
                constraint_details={
                    "format": "uuid",
                    "expected_length": SwaggerConstants.UUID_LENGTH,
                    "actual_length": len(SwaggerConstants.UUID_TOO_LONG_EXAMPLE)
                },
                rationale=f"Tests invalid partition where UUID length > {SwaggerConstants.UUID_LENGTH} characters"
            )
        ])
        
        return partitions


class EmailPartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for email format validation."""
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid email partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_email",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description="Valid: correctly formatted email",
            test_value=SwaggerConstants.VALID_EMAIL_EXAMPLE,
            constraint_details={"format": "email"},
            rationale="Tests valid partition with correct email format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid email partitions."""
        partitions = []
        
        for idx, invalid_email in enumerate(SwaggerConstants.INVALID_EMAIL_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_email{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed email ({invalid_email or 'empty'})",
                test_value=invalid_email,
                constraint_details={"format": "email"},
                rationale="Tests invalid partition with incorrect email format"
            ))
        
        return partitions


class DatePartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for date/date-time format validation."""
    
    def __init__(self, format_type: str = "date"):
        """Initialize with specific date format type."""
        self.format_type = format_type
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid date partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_date",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description=f"Valid: correctly formatted {self.format_type}",
            test_value=SwaggerConstants.VALID_DATE_EXAMPLE,
            constraint_details={"format": self.format_type},
            rationale=f"Tests valid partition with correct {self.format_type} format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid date partitions."""
        partitions = []
        
        for idx, invalid_date in enumerate(SwaggerConstants.INVALID_DATE_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_date{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed {self.format_type} ({invalid_date or 'empty'})",
                test_value=invalid_date,
                constraint_details={"format": self.format_type},
                rationale=f"Tests invalid partition with incorrect {self.format_type} format"
            ))
        
        return partitions


class URIPartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for URI/URL format validation."""
    
    def __init__(self, format_type: str = "uri"):
        """Initialize with specific URI format type."""
        self.format_type = format_type
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid URI partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_uri",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description=f"Valid: correctly formatted {self.format_type}",
            test_value=SwaggerConstants.VALID_URI_EXAMPLE,
            constraint_details={"format": self.format_type},
            rationale=f"Tests valid partition with correct {self.format_type} format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid URI partitions."""
        partitions = []
        
        for idx, invalid_uri in enumerate(SwaggerConstants.INVALID_URI_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_uri{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed {self.format_type} ({invalid_uri or 'empty'})",
                test_value=invalid_uri,
                constraint_details={"format": self.format_type},
                rationale=f"Tests invalid partition with incorrect {self.format_type} format"
            ))
        
        return partitions


class IPv4PartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for IPv4 format validation."""
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid IPv4 partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_ipv4",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description="Valid: correctly formatted IPv4 address",
            test_value=SwaggerConstants.VALID_IPV4_EXAMPLE,
            constraint_details={"format": "ipv4"},
            rationale="Tests valid partition with correct IPv4 format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid IPv4 partitions."""
        partitions = []
        
        for idx, invalid_ip in enumerate(SwaggerConstants.INVALID_IPV4_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_ipv4{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed IPv4 address ({invalid_ip or 'empty'})",
                test_value=invalid_ip,
                constraint_details={"format": "ipv4"},
                rationale="Tests invalid partition with incorrect IPv4 format"
            ))
        
        return partitions


class IPv6PartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for IPv6 format validation."""
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid IPv6 partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_ipv6",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description="Valid: correctly formatted IPv6 address",
            test_value=SwaggerConstants.VALID_IPV6_EXAMPLE,
            constraint_details={"format": "ipv6"},
            rationale="Tests valid partition with correct IPv6 format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid IPv6 partitions."""
        partitions = []
        
        for idx, invalid_ip in enumerate(SwaggerConstants.INVALID_IPV6_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_ipv6{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed IPv6 address ({invalid_ip or 'empty'})",
                test_value=invalid_ip,
                constraint_details={"format": "ipv6"},
                rationale="Tests invalid partition with incorrect IPv6 format"
            ))
        
        return partitions


class HostnamePartitionGenerator(FormatPartitionGenerator):
    """Generates partitions for hostname format validation."""
    
    def generate_valid_partition(
        self,
        field_name: str,
        partition_id_base: str
    ) -> EquivalencePartition:
        """Generate valid hostname partition."""
        return EquivalencePartition(
            partition_id=f"{partition_id_base}valid_hostname",
            partition_type=PartitionType.VALID,
            category=PartitionCategory.FORMAT,
            field_name=field_name,
            description="Valid: correctly formatted hostname",
            test_value=SwaggerConstants.VALID_HOSTNAME_EXAMPLE,
            constraint_details={"format": "hostname"},
            rationale="Tests valid partition with correct hostname format"
        )
    
    def generate_invalid_partitions(
        self,
        field_name: str,
        partition_id_base: str
    ) -> List[EquivalencePartition]:
        """Generate invalid hostname partitions."""
        partitions = []
        
        for idx, invalid_host in enumerate(SwaggerConstants.INVALID_HOSTNAME_EXAMPLES):
            partitions.append(EquivalencePartition(
                partition_id=f"{partition_id_base}invalid_hostname{idx}",
                partition_type=PartitionType.INVALID,
                category=PartitionCategory.FORMAT,
                field_name=field_name,
                description=f"Invalid: malformed hostname ({invalid_host or 'empty'})",
                test_value=invalid_host,
                constraint_details={"format": "hostname"},
                rationale="Tests invalid partition with incorrect hostname format"
            ))
        
        return partitions


class FormatPartitionGeneratorFactory:
    """
    Factory for creating format-specific partition generators.
    
    Follows Factory Pattern - creates appropriate generator based on format type.
    Follows Open/Closed Principle - easy to add new formats without modifying existing code.
    """
    
    @staticmethod
    def create_generator(format_type: str) -> FormatPartitionGenerator:
        """
        Create appropriate partition generator for format type.
        
        Args:
            format_type: Format string from swagger (uuid, email, date, etc.)
            
        Returns:
            FormatPartitionGenerator instance
            
        Raises:
            ValueError: If format type is not supported
        """
        generators = {
            "uuid": UUIDPartitionGenerator(),
            "email": EmailPartitionGenerator(),
            "date": DatePartitionGenerator("date"),
            "date-time": DatePartitionGenerator("date-time"),
            "uri": URIPartitionGenerator("uri"),
            "url": URIPartitionGenerator("url"),
            "ipv4": IPv4PartitionGenerator(),
            "ipv6": IPv6PartitionGenerator(),
            "hostname": HostnamePartitionGenerator(),
        }
        
        generator = generators.get(format_type.lower())
        if not generator:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        return generator
