"""
Unified Test Generation Service
Orchestrates multiple testing techniques (EP, BVA) and merges results.
Respects SRP: Single responsibility of coordinating test generation.
Respects DIP: Depends on abstractions (repositories), not concrete implementations.
"""

from typing import List, Dict, Any
from pathlib import Path
import json

from ..domain.models import UnifiedTestResult
from .equivalence_partitioning.services import EquivalencePartitionService
from .boundary_value_analysis.services import BVAService
from .decision_table.services import DecisionTableService


class UnifiedTestGenerationService:
    """
    Application service that orchestrates multiple test generation techniques.
    
    Responsibilities:
    - Coordinate EP and BVA services
    - Merge results from multiple techniques
    - Ensure output consistency
    
    Respects Open/Closed: New techniques can be added without modifying existing code.
    Respects SRP: Single responsibility of coordinating test generation.
    Respects DIP: Depends on abstractions (services), not concrete implementations.
    """
    
    def __init__(
        self,
        ep_service: EquivalencePartitionService,
        bva_service: BVAService,
        dt_service: DecisionTableService = None
    ):
        """
        Dependency Injection: Services injected (DIP principle).
        
        Args:
            ep_service: Equivalence Partitioning service
            bva_service: Boundary Value Analysis service
            dt_service: Decision Table service (optional)
        """
        self._ep_service = ep_service
        self._bva_service = bva_service
        self._dt_service = dt_service or DecisionTableService()
    
    async def generate_all_techniques(
        self,
        swagger_analysis_file: str,
        techniques: List[str] = None,
        bva_version: str = "both",
        endpoint_filter: str = None,
        method_filter: str = None,
        save_output: bool = True,
        output_directory: Path = None
    ) -> List[UnifiedTestResult]:
        """
        Generate test cases using multiple techniques and merge results.
        
        Args:
            swagger_analysis_file: Path to swagger analysis JSON
            techniques: List of techniques to apply (default: all available)
            bva_version: "2-value", "3-value", or "both"
            endpoint_filter: Optional endpoint path filter
            method_filter: Optional HTTP method filter
            save_output: Whether to save results to files
            output_directory: Custom output directory
            
        Returns:
            Unified results containing all techniques
        """
        if techniques is None:
            techniques = ["equivalence_partitioning", "boundary_value_analysis", "decision_table"]
        
        # Container for unified results
        unified_results: List[UnifiedTestResult] = []
        
        # Apply Equivalence Partitioning if requested
        ep_results_dict = {}
        if "equivalence_partitioning" in techniques:
            ep_results_list = await self._ep_service.generate_test_cases_from_json(
                swagger_analysis_file=swagger_analysis_file,
                endpoint_filter=endpoint_filter,
                method_filter=method_filter
            )
            
            # Index by endpoint key
            for ep_result in ep_results_list:
                key = f"{ep_result.http_method}_{ep_result.endpoint}"
                ep_results_dict[key] = ep_result
        
        # Apply Boundary Value Analysis if requested
        bva_results_dict = {}
        if "boundary_value_analysis" in techniques:
            bva_versions = ["2-value", "3-value"] if bva_version == "both" else [bva_version]
            
            for version in bva_versions:
                bva_results_list = await self._bva_service.generate_bva_tests(
                    swagger_analysis_file=swagger_analysis_file,
                    bva_version=version,
                    endpoint_filter=endpoint_filter,
                    method_filter=method_filter
                )
                
                # Index by endpoint key and version
                for bva_result in bva_results_list:
                    key = f"{bva_result.http_method}_{bva_result.endpoint}"
                    if key not in bva_results_dict:
                        bva_results_dict[key] = []
                    bva_results_dict[key].append(bva_result)
        
        # Apply Decision Table if requested
        dt_results_dict = {}
        if "decision_table" in techniques:
            dt_results_list = await self._dt_service.generate_decision_table_tests(
                swagger_analysis_file=swagger_analysis_file,
                endpoint_filter=endpoint_filter,
                method_filter=method_filter
            )
            
            # Index by endpoint key
            for dt_result in dt_results_list:
                key = f"{dt_result.http_method}_{dt_result.endpoint}"
                dt_results_dict[key] = dt_result
        
        # Merge results by endpoint
        all_keys = set(ep_results_dict.keys()) | set(bva_results_dict.keys()) | set(dt_results_dict.keys())
        
        for key in all_keys:
            # Extract endpoint and method from key
            parts = key.split("_", 1)
            method = parts[0]
            endpoint = parts[1] if len(parts) > 1 else ""
            
            # Create unified result for this endpoint
            unified = UnifiedTestResult(
                endpoint=endpoint,
                http_method=method
            )
            
            # Add EP results if available
            if key in ep_results_dict:
                unified.add_ep_result(ep_results_dict[key])
            
            # Add BVA results if available
            if key in bva_results_dict:
                for bva_result in bva_results_dict[key]:
                    unified.add_bva_result(bva_result)
            
            # Add Decision Table results if available
            if key in dt_results_dict:
                unified.add_dt_result(dt_results_dict[key])
            
            unified_results.append(unified)
        
        # Save unified results if requested
        if save_output:
            from src.shared.mappers.test_case_mapper import TestCaseMapper
            TestCaseMapper.save_unified_to_json(unified_results, swagger_analysis_file)
        
        return unified_results
    

