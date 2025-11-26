"""Mapper for converting test generation models to JSON-serializable dictionaries."""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

from src.tools.test_generation.domain.models import (
    TestGenerationResult, TestCase, EquivalencePartition, PartitionSet
)
from src.tools.test_generation.infrastructure.filename_generator import FilenameGenerator
from src.tools.test_generation.infrastructure.filename_generator import FilenameGenerator


class TestCaseMapper:
    """Mapper for converting test case models to dictionaries."""
    
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
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize filename generator (follows SOLID: Single Responsibility)
        filename_gen = FilenameGenerator()
        
        saved_files = []
        
        # Create one file per endpoint
        for result in results:
            # Generate camelCase filename: postBeneficiarios.json, getBeneficiariosId.json
            filename_base = filename_gen.generate(result.http_method, result.endpoint)
            filename = f"{filename_base}.json"
            file_path = output_dir / filename
            
            # Separate test cases into success and failure
            success_cases = [
                tc for tc in result.test_cases 
                if tc.expected_status_code in [200, 201, 204]
            ]
            failure_cases = [
                tc for tc in result.test_cases 
                if tc.expected_status_code not in [200, 201, 204]
            ]
            
            # Prepare endpoint data with grouped test cases
            output_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "source_file": source_file,
                    "technique": "Equivalence Partitioning (ISTQB v4)",
                    "endpoint": result.endpoint,
                    "http_method": result.http_method,
                    "tool_version": "1.0.0"
                },
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
            
            # Write JSON file for this endpoint
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            saved_files.append(file_path)
        
        return saved_files