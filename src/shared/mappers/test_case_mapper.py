"""Mapper for converting test generation models to JSON-serializable dictionaries.

Supports both single-technique and unified multi-technique test results.
Respects Open/Closed Principle: extensible for new techniques without modification.
"""
from typing import Dict, Any, List, Union
from pathlib import Path

from src.tools.test_generation.domain.models import (
    TestGenerationResult, TestCase, EquivalencePartition, PartitionSet,
    BVAResult, BVATestCase, BoundaryValue,
    UnifiedTestCase, UnifiedTestResult
)
from src.tools.test_generation.infrastructure.equivalence_partitioning.filename_generator import FilenameGenerator
from src.shared.utils.file_operations import FileOperations
from src.shared.constants import HTTPStatus, TestingTechniques


class TestCaseMapper:
    """
    Mapper for converting test case models to dictionaries.
    
    Supports:
    - Single technique results (EP or BVA)
    - Unified multi-technique results (EP + BVA 2-value + BVA 3-value)
    - Maintains backwards compatibility with karate_generation tool
    """
    
    @staticmethod
    def to_dict(result: TestGenerationResult) -> Dict[str, Any]:
        """
        Convert TestGenerationResult to dictionary.
        
        Args:
            result: TestGenerationResult domain model
            
        Returns:
            Dictionary representation for JSON serialization
        """
        return {
            "endpoint": result.endpoint,
            "http_method": result.http_method,
            "technique": result.technique,
            "metrics": {
                "total_partitions": result.total_partitions,
                "valid_partitions": result.valid_partitions,
                "invalid_partitions": result.invalid_partitions,
                "coverage_percentage": round(result.coverage_percentage, 2)
            },
            "partition_sets": [
                TestCaseMapper._map_partition_set(ps) for ps in result.partition_sets
            ],
            "test_cases": [
                TestCaseMapper._map_test_case(tc) for tc in result.test_cases
            ],
            "summary": result.summary
        }
    
    @staticmethod
    def to_dict_list(results: List[TestGenerationResult]) -> List[Dict[str, Any]]:
        """Convert list of TestGenerationResult to list of dictionaries."""
        return [TestCaseMapper.to_dict(result) for result in results]
    
    @staticmethod
    def _map_partition_set(partition_set: PartitionSet) -> Dict[str, Any]:
        """Map PartitionSet to dictionary."""
        return {
            "field_name": partition_set.field_name,
            "field_type": partition_set.field_type,
            "total_partitions": len(partition_set.partitions),
            "valid_partitions_count": len(partition_set.get_valid_partitions()),
            "invalid_partitions_count": len(partition_set.get_invalid_partitions()),
            "partitions": [
                TestCaseMapper._map_partition(p) for p in partition_set.partitions
            ]
        }
    
    @staticmethod
    def _map_partition(partition: EquivalencePartition) -> Dict[str, Any]:
        """Map EquivalencePartition to dictionary."""
        return {
            "partition_id": partition.partition_id,
            "partition_type": partition.partition_type.value,
            "category": partition.category.value,
            "field_name": partition.field_name,
            "description": partition.description,
            "test_value": partition.test_value,
            "constraint_details": partition.constraint_details,
            "rationale": partition.rationale
        }
    
    @staticmethod
    def _map_test_case(test_case: TestCase) -> Dict[str, Any]:
        """Map TestCase to dictionary."""
        return {
            "test_case_id": test_case.test_case_id,
            "test_name": test_case.test_name,
            "technique": test_case.technique,
            "endpoint": test_case.endpoint,
            "http_method": test_case.http_method,
            "priority": test_case.priority.value,
            "objective": test_case.objective,
            "test_data": test_case.test_data,
            "expected_result": test_case.expected_result,
            "expected_status_code": test_case.expected_status_code,
            "preconditions": test_case.preconditions,
            "steps": test_case.steps,
            "tags": test_case.tags,
            "partitions_covered": [
                {
                    "partition_id": p.partition_id,
                    "field_name": p.field_name,
                    "partition_type": p.partition_type.value,
                    "category": p.category.value
                }
                for p in test_case.partitions_covered
            ]
        }
    
    @staticmethod
    def save_to_json(results: List[TestGenerationResult], source_file: str) -> List[Path]:
        """
        Save test generation results to separate JSON files per endpoint.
        Each file contains success and failure test cases grouped separately.
        
        Args:
            results: List of TestGenerationResult
            source_file: Source swagger analysis file path
            
        Returns:
            List of paths to the saved JSON files (one per endpoint)
        """
        # Create output directory
        output_dir = Path("output") / "test_cases"
        
        # Initialize filename generator (follows SOLID: Single Responsibility)
        filename_gen = FilenameGenerator()
        
        saved_files = []
        
        # Create one file per endpoint
        for result in results:
            # Generate camelCase filename: postBeneficiarios.json, getBeneficiariosId.json
            filename_base = filename_gen.generate(result.http_method, result.endpoint)
            filename = f"{filename_base}.json"
            file_path = output_dir / filename
            
            # Separate test cases into success and failure using constants
            success_cases = [
                tc for tc in result.test_cases 
                if tc.expected_status_code in HTTPStatus.SUCCESS_CODES
            ]
            failure_cases = [
                tc for tc in result.test_cases 
                if tc.expected_status_code not in HTTPStatus.SUCCESS_CODES
            ]
            
            # Create metadata using FileOperations
            metadata = FileOperations.create_metadata(
                source=source_file,
                technique="Equivalence Partitioning (ISTQB v4)",
                additional_fields={
                    "endpoint": result.endpoint,
                    "http_method": result.http_method
                }
            )
            
            # Prepare endpoint data with grouped test cases
            output_data = {
                "metadata": metadata,
                "metrics": {
                    "total_partitions": result.total_partitions,
                    "valid_partitions": result.valid_partitions,
                    "invalid_partitions": result.invalid_partitions,
                    "coverage_percentage": round(result.coverage_percentage, 2),
                    "total_test_cases": len(result.test_cases),
                    "success_test_cases": len(success_cases),
                    "failure_test_cases": len(failure_cases)
                },
                "partition_sets": [
                    TestCaseMapper._map_partition_set(ps) for ps in result.partition_sets
                ],
                "success_test_cases": [
                    TestCaseMapper._map_test_case(tc) for tc in success_cases
                ],
                "failure_test_cases": [
                    TestCaseMapper._map_test_case(tc) for tc in failure_cases
                ],
                "summary": result.summary
            }
            
            # Use FileOperations to save JSON
            FileOperations.save_json(output_data, file_path)
            saved_files.append(file_path)
        
        return saved_files
    
    @staticmethod
    def to_unified_dict(result: UnifiedTestResult) -> Dict[str, Any]:
        """
        Convert UnifiedTestResult (multiple techniques) to dictionary.
        
        Maintains backwards compatibility with karate_generation tool:
        - Same structure as single-technique output
        - success_test_cases and failure_test_cases fields
        - All techniques merged into single test case list
        
        Args:
            result: UnifiedTestResult containing EP and/or BVA cases
            
        Returns:
            Dictionary for JSON serialization
        """
        # Separate by expected status code using constants
        success_cases = [
            tc for tc in result.test_cases
            if tc.expected_status_code in HTTPStatus.SUCCESS_CODES
        ]
        failure_cases = [
            tc for tc in result.test_cases
            if tc.expected_status_code not in HTTPStatus.SUCCESS_CODES
        ]
        
        return {
            "metadata": {
                "generated_at": result.generated_at,
                "endpoint": result.endpoint,
                "http_method": result.http_method,
                "techniques": result.techniques_applied,
                "tool_version": "1.0.0"
            },
            "metrics": {
                **result.get_metrics_summary(),
                "total_test_cases": len(result.test_cases),
                "success_test_cases": len(success_cases),
                "failure_test_cases": len(failure_cases)
            },
            "success_test_cases": [
                TestCaseMapper._map_unified_test_case(tc) for tc in success_cases
            ],
            "failure_test_cases": [
                TestCaseMapper._map_unified_test_case(tc) for tc in failure_cases
            ]
        }
    
    @staticmethod
    def _map_unified_test_case(test_case: UnifiedTestCase) -> Dict[str, Any]:
        """
        Map UnifiedTestCase to dictionary.
        
        Maintains structure compatible with karate_generation tool.
        Handles all complex object serialization (enums, nested objects).
        """
        # Handle priority - convert enum to string if needed
        priority_value = test_case.priority
        if hasattr(priority_value, 'value'):
            priority_value = priority_value.value
        
        base = {
            "test_case_id": test_case.test_case_id,
            "test_name": test_case.test_name,
            "technique": test_case.technique,
            "endpoint": test_case.endpoint,
            "http_method": test_case.http_method,
            "priority": priority_value,
            "objective": test_case.objective,
            "test_data": test_case.test_data,
            "expected_result": test_case.expected_result,
            "expected_status_code": test_case.expected_status_code,
            "tags": test_case.tags
        }
        
        # Add optional fields if present
        if test_case.expected_error:
            base["expected_error"] = test_case.expected_error
        if test_case.preconditions:
            base["preconditions"] = test_case.preconditions
        if test_case.steps:
            base["steps"] = test_case.steps
        if test_case.metadata:
            # Serialize metadata - handle complex objects
            base["metadata"] = TestCaseMapper._serialize_metadata(test_case.metadata)
        
        return base
    
    @staticmethod
    def _serialize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize metadata dictionary to JSON-compatible format.
        Handles EquivalencePartition and other complex objects.
        """
        serialized = {}
        
        for key, value in metadata.items():
            if key == "partitions_covered" and isinstance(value, list):
                # Serialize list of EquivalencePartition objects
                serialized[key] = [
                    {
                        "partition_id": p.partition_id,
                        "field_name": p.field_name,
                        "partition_type": p.partition_type.value if hasattr(p.partition_type, 'value') else str(p.partition_type),
                        "category": p.category.value if hasattr(p.category, 'value') else str(p.category)
                    }
                    for p in value
                ]
            elif hasattr(value, '__dict__'):
                # Generic object serialization
                serialized[key] = {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
            elif hasattr(value, 'value'):
                # Enum serialization
                serialized[key] = value.value
            else:
                # Simple value
                serialized[key] = value
        
        return serialized
    
    @staticmethod
    def save_unified_to_json(
        results: List[UnifiedTestResult], 
        source_file: str
    ) -> List[Path]:
        """
        Save unified test results to JSON files (one per endpoint).
        
        Each file contains test cases from all applied techniques:
        - Equivalence Partitioning
        - Boundary Value Analysis (2-value)
        - Boundary Value Analysis (3-value)
        
        Args:
            results: List of UnifiedTestResult
            source_file: Source swagger analysis file path
            
        Returns:
            List of paths to saved JSON files
        """
        output_dir = Path("output") / "test_cases"
        
        filename_gen = FilenameGenerator()
        saved_files = []
        
        for result in results:
            # Generate consistent filename: {method}{endpoint}.json
            filename_base = filename_gen.generate(result.http_method, result.endpoint)
            filename = f"{filename_base}.json"
            file_path = output_dir / filename
            
            # Convert to dict and add source file
            output_data = TestCaseMapper.to_unified_dict(result)
            output_data["metadata"]["source_file"] = source_file
            
            # Use FileOperations to save JSON
            FileOperations.save_json(output_data, file_path)
            saved_files.append(file_path)
        
        return saved_files