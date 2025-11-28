"""MCP tools orchestrator for Swagger Analysis and Test Generation."""
from typing import Dict, Any
from pathlib import Path

# Import swagger analysis services
from src.tools.swagger_analysis.application.services import SwaggerAnalysisService
from src.tools.swagger_analysis.infrastructure.repositories import HttpSwaggerRepository
from src.tools.swagger_analysis.domain.exceptions import SwaggerAnalysisError
from src.shared.mappers.swagger_mapper import SwaggerMapper

# Import test generation services
from src.tools.test_generation.application.equivalence_partitioning.services import EquivalencePartitionService
from src.tools.test_generation.application.boundary_value_analysis.services import BVAService
from src.tools.test_generation.domain.exceptions import TestGenerationError
from src.tools.test_generation.domain.boundary_value_analysis.exceptions import BVAError
from src.shared.mappers.test_case_mapper import TestCaseMapper

# Import karate generation services
from src.tools.karate_generation.application.services import KarateGenerationService
from src.tools.karate_generation.infrastructure.repositories import FileKarateRepository
from src.tools.karate_generation.domain.exceptions import KarateGenerationError


class MCPToolsOrchestrator:
    """Orchestrator for Swagger Analysis and Test Generation tools."""
    
    def __init__(self):
        # Initialize swagger analysis
        self.swagger_repo = HttpSwaggerRepository()
        self.swagger_service = SwaggerAnalysisService(self.swagger_repo)
        
        # Initialize test generation
        self.test_generation_service = EquivalencePartitionService()
        self.bva_service = BVAService()
        
        # Initialize karate generation
        self.karate_repo = FileKarateRepository()
        self.karate_service = KarateGenerationService(self.karate_repo)
    
    async def analyze_swagger_from_url(
        self, 
        swagger_url: str,
        save_output: bool = True,
        output_format: str = "both"
    ) -> Dict[str, Any]:
        """
        Tool: Analyze swagger specification from URL.
        
        Args:
            swagger_url: URL to the swagger/OpenAPI specification
            save_output: Whether to save output to JSON file
            output_format: Output format - 'console', 'file', or 'both'
            
        Returns:
            Comprehensive swagger analysis result with detailed validation info
        """
        try:
            # Use swagger analysis service
            result = await self.swagger_service.analyze_swagger(swagger_url)
            
            # Convert using the new mapper
            result_dict = SwaggerMapper.to_dict(result)
            
            response = {
                "success": True,
                "data": result_dict,
                "message": f"Successfully analyzed {result.total_endpoints} endpoints from swagger specification"
            }
            
            # Save to file if requested
            if save_output and output_format in ["file", "both"]:
                file_path = SwaggerMapper.save_to_json(result_dict, swagger_url)
                response["output_file"] = str(file_path)
                response["message"] += f" | Output saved to: {file_path}"
            
            return response
            
        except SwaggerAnalysisError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "SwaggerAnalysisError",
                "message": f"Failed to analyze swagger specification: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError",
                "message": f"Unexpected error during swagger analysis: {str(e)}"
            }
    
    async def generate_equivalence_partition_tests(
        self,
        swagger_analysis_file: str,
        endpoint_filter: str = None,
        method_filter: str = None,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Tool: Generate test cases using Equivalence Partitioning (ISTQB v4).
        
        Takes swagger analysis JSON as input and generates test cases that cover
        all identified equivalence partitions (valid and invalid).
        
        Args:
            swagger_analysis_file: Path to swagger analysis JSON file
            endpoint_filter: Optional - filter by specific endpoint
            method_filter: Optional - filter by HTTP method (GET, POST, etc.)
            save_output: Whether to save test cases to JSON file
            
        Returns:
            Test generation results with all test cases and coverage metrics
        """
        try:
            # Generate test cases
            results = await self.test_generation_service.generate_test_cases_from_json(
                swagger_analysis_file=swagger_analysis_file,
                endpoint_filter=endpoint_filter,
                method_filter=method_filter
            )
            
            # Convert to dictionary
            results_dict = TestCaseMapper.to_dict_list(results)
            
            # Calculate totals
            total_test_cases = sum(len(r.test_cases) for r in results)
            total_partitions = sum(r.total_partitions for r in results)
            avg_coverage = sum(r.coverage_percentage for r in results) / len(results) if results else 0
            
            response = {
                "success": True,
                "data": results_dict,
                "summary": {
                    "total_endpoints": len(results),
                    "total_test_cases": total_test_cases,
                    "total_partitions": total_partitions,
                    "average_coverage": round(avg_coverage, 2),
                    "technique": "Equivalence Partitioning (ISTQB v4)"
                },
                "message": f"Successfully generated {total_test_cases} test cases for {len(results)} endpoints"
            }
            
            # Save to files if requested (one per endpoint)
            if save_output:
                file_paths = TestCaseMapper.save_to_json(results, swagger_analysis_file)
                response["output_files"] = [str(fp) for fp in file_paths]
                response["message"] += f" | Output saved to {len(file_paths)} files"
            
            return response
            
        except TestGenerationError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "TestGenerationError",
                "message": f"Failed to generate test cases: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError",
                "message": f"Unexpected error during test case generation: {str(e)}"
            }
    
    async def generate_karate_features(
        self,
        test_cases_directory: str,
        base_url: str = "http://localhost:8080",
        output_directory: str = None
    ) -> Dict[str, Any]:
        """
        Tool: Generate Karate feature files from test cases.
        
        Takes test case JSON files and generates Karate feature files with:
        - Gherkin syntax (Given-When-Then)
        - Scenario Outline for data-driven tests
        - @smoke tags for success scenarios
        - @regression, @negative tags for failure scenarios
        - karate-config.js with headers and helpers
        
        Args:
            test_cases_directory: Directory containing test case JSON files
            base_url: Base URL for API (default: http://localhost:8080)
            output_directory: Output directory for features (default: output/functional)
            
        Returns:
            Generation results with feature file paths and summary
        """
        try:
            # Setup paths
            test_cases_dir = Path(test_cases_directory)
            if not test_cases_dir.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {test_cases_directory}",
                    "error_type": "DirectoryNotFoundError",
                    "message": "Test cases directory does not exist"
                }
            
            # Default output directory
            if output_directory is None:
                output_directory = "output/functional"
            
            output_dir = Path(output_directory)
            
            # Generate features
            result = self.karate_service.generate_features_from_directory(
                test_cases_dir=test_cases_dir,
                output_dir=output_dir,
                base_url=base_url
            )
            
            if result.success:
                response = {
                    "success": True,
                    "data": result.to_dict(),
                    "message": (
                        f"Successfully generated {len(result.features_generated)} Karate features "
                        f"with {result.total_scenarios} scenarios and {result.total_examples} test cases"
                    )
                }
                
                if result.errors:
                    response["warnings"] = result.errors
                
                return response
            else:
                return {
                    "success": False,
                    "error": "; ".join(result.errors),
                    "error_type": "KarateGenerationError",
                    "message": "Failed to generate Karate features",
                    "details": result.to_dict()
                }
        
        except KarateGenerationError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "KarateGenerationError",
                "message": f"Failed to generate Karate features: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError",
                "message": f"Unexpected error during Karate feature generation: {str(e)}"
            }
    
    async def generate_boundary_value_tests(
        self,
        swagger_analysis_file: str,
        bva_version: str = "2-value",
        endpoint_filter: str = None,
        method_filter: str = None,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Tool: Generate test cases using Boundary Value Analysis (ISTQB v4).
        
        Applies BVA to ordered partitions (string length, numeric ranges, array counts).
        Supports both 2-value BVA (boundary + 1 neighbor) and 3-value BVA (boundary + 2 neighbors).
        
        Args:
            swagger_analysis_file: Path to swagger analysis JSON file
            bva_version: "2-value" or "3-value" BVA (default: "2-value")
            endpoint_filter: Optional - filter by specific endpoint
            method_filter: Optional - filter by HTTP method
            save_output: Whether to save test cases to JSON file
            
        Returns:
            BVA test generation results with coverage metrics
        """
        try:
            # Generate BVA test cases
            results = await self.bva_service.generate_bva_tests(
                swagger_analysis_file=swagger_analysis_file,
                bva_version=bva_version,
                endpoint_filter=endpoint_filter,
                method_filter=method_filter
            )
            
            # Convert to dictionary
            results_dict = self._bva_results_to_dict(results)
            
            # Calculate totals
            total_test_cases = sum(len(r.test_cases) for r in results)
            total_boundaries = sum(r.boundaries_identified for r in results)
            avg_coverage = sum(r.coverage_percentage for r in results) / len(results) if results else 0
            
            response = {
                "success": True,
                "data": results_dict,
                "summary": {
                    "total_endpoints": len(results),
                    "total_test_cases": total_test_cases,
                    "total_boundaries": total_boundaries,
                    "average_coverage": round(avg_coverage, 2),
                    "technique": f"Boundary Value Analysis ({bva_version}) - ISTQB v4"
                },
                "message": f"Successfully generated {total_test_cases} BVA test cases for {len(results)} endpoints"
            }
            
            # Save to files if requested
            if save_output:
                file_paths = self._save_bva_results(results, swagger_analysis_file)
                response["output_files"] = [str(fp) for fp in file_paths]
                response["message"] += f" | Output saved to {len(file_paths)} files"
            
            return response
            
        except BVAError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "BVAError",
                "message": f"BVA generation failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError",
                "message": f"Unexpected error during BVA generation: {str(e)}"
            }
    
    def _bva_results_to_dict(self, results: list) -> list:
        """Convert BVA results to dictionary format."""
        return [{
            "endpoint": r.endpoint,
            "http_method": r.http_method,
            "bva_version": r.bva_version,
            "boundaries_identified": r.boundaries_identified,
            "coverage_percentage": round(r.coverage_percentage, 2),
            "coverage_items_tested": r.coverage_items_tested,
            "coverage_items_total": r.coverage_items_total,
            "metadata": r.metadata,
            "test_cases": [{
                "test_case_id": tc.test_case_id,
                "test_name": tc.test_name,
                "test_data": tc.test_data,
                "expected_status_code": tc.expected_status_code,
                "expected_error": tc.expected_error,
                "boundary_info": tc.boundary_info,
                "priority": tc.priority
            } for tc in r.test_cases]
        } for r in results]
    
    def _save_bva_results(self, results: list, swagger_file: str) -> list:
        """Save BVA results to JSON files."""
        import json
        from datetime import datetime
        
        swagger_path = Path(swagger_file)
        output_dir = swagger_path.parent.parent / "bva_tests"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for result in results:
            # Generate filename
            endpoint_name = result.endpoint.replace("/", "_").replace("{", "").replace("}", "")
            if endpoint_name.startswith("_"):
                endpoint_name = endpoint_name[1:]
            
            filename = f"{result.http_method.lower()}{endpoint_name}_{result.bva_version}_{timestamp}.json"
            file_path = output_dir / filename
            
            # Prepare output data
            output_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "source_file": str(swagger_path),
                    "technique": f"Boundary Value Analysis ({result.bva_version}) - ISTQB v4",
                    "endpoint": result.endpoint,
                    "http_method": result.http_method,
                    "tool_version": "1.0.0"
                },
                "metrics": {
                    "boundaries_identified": result.boundaries_identified,
                    "coverage_percentage": round(result.coverage_percentage, 2),
                    "coverage_items_tested": result.coverage_items_tested,
                    "coverage_items_total": result.coverage_items_total,
                    "total_test_cases": len(result.test_cases)
                },
                "test_cases": [{
                    "test_case_id": tc.test_case_id,
                    "test_name": tc.test_name,
                    "test_data": tc.test_data,
                    "expected_status_code": tc.expected_status_code,
                    "expected_error": tc.expected_error,
                    "boundary_info": tc.boundary_info,
                    "bva_version": tc.bva_version,
                    "priority": tc.priority
                } for tc in result.test_cases]
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            file_paths.append(file_path)
        
        return file_paths