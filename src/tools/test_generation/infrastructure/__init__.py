"""Infrastructure layer for test generation - refactored with SOLID principles."""

# Refactored implementations (recommended)
from .partition_identifier_refactored import PartitionIdentifierRefactored
from .test_case_builder_refactored import TestCaseBuilderRefactored
from .status_code_resolver import StatusCodeResolver
from .error_code_resolver import ErrorCodeResolver

# Specialized generators
from .format_partition_factory import (
    FormatPartitionGeneratorFactory,
    FormatPartitionGenerator,
    UUIDPartitionGenerator,
    EmailPartitionGenerator,
    DatePartitionGenerator,
    URIPartitionGenerator,
    IPv4PartitionGenerator,
    IPv6PartitionGenerator,
    HostnamePartitionGenerator
)

from .constraint_partition_generators import (
    LengthPartitionGenerator,
    RangePartitionGenerator,
    EnumPartitionGenerator,
    RequiredPartitionGenerator,
    TypePartitionGenerator
)

__all__ = [
    # Refactored (recommended)
    "PartitionIdentifierRefactored",
    "TestCaseBuilderRefactored",
    "StatusCodeResolver",
    "ErrorCodeResolver",
    
    # Factories and Generators
    "FormatPartitionGeneratorFactory",
    "FormatPartitionGenerator",
    "UUIDPartitionGenerator",
    "EmailPartitionGenerator",
    "DatePartitionGenerator",
    "URIPartitionGenerator",
    "IPv4PartitionGenerator",
    "IPv6PartitionGenerator",
    "HostnamePartitionGenerator",
    "LengthPartitionGenerator",
    "RangePartitionGenerator",
    "EnumPartitionGenerator",
    "RequiredPartitionGenerator",
    "TypePartitionGenerator",
]