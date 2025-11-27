"""
Application services for Karate feature generation.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from ..domain.models import (
    KarateFeature,
    KarateScenario,
    KarateExample,
    KarateConfig,
    KarateGenerationResult,
    ScenarioType,
    HttpMethod
)
from ..domain.repositories import KarateGeneratorRepository
from ..domain.exceptions import KarateGenerationError
from ..domain.value_objects import EnvironmentGenerator, HeaderExtractor
from ..config import PATH_CONFIG, CONFIG_DEFAULTS


class KarateGenerationService:
    """Service for generating Karate features from test cases."""
    
    def __init__(self, repository: KarateGeneratorRepository):
        self.repository = repository
        self.path_config = PATH_CONFIG
        self.config_defaults = CONFIG_DEFAULTS
    
    def generate_features_from_directory(
        self, 
        test_cases_dir: Path, 
        output_dir: Path,
        base_url: Optional[str] = None
    ) -> KarateGenerationResult:
        """
        Generate Karate features from all test case files in directory.
        
        Args:
            test_cases_dir: Directory containing test case JSON files
            output_dir: Output directory for Karate features
            base_url: Base URL for API (if not provided, will be extracted from test case metadata)
            
        Returns:
            KarateGenerationResult with generation summary
        """
        features_generated = []
        total_scenarios = 0
        total_examples = 0
        errors = []
        
        try:
            # List all test case files
            test_case_files = self.repository.list_test_case_files(test_cases_dir)
            
            if not test_case_files:
                return KarateGenerationResult(
                    success=False,
                    features_generated=[],
                    config_file="",
                    total_scenarios=0,
                    total_examples=0,
                    errors=["No test case files found"]
                )
            
            # Extract base_url from swagger analysis if not provided
            if base_url is None:
                base_url = self._extract_base_url_from_test_files(test_case_files)
                if base_url is None:
                    return KarateGenerationResult(
                        success=False,
                        features_generated=[],
                        config_file="",
                        total_scenarios=0,
                        total_examples=0,
                        errors=["base_url not provided and could not be extracted from test case metadata"]
                    )
            
            # Create output directory structure
            functional_dir = self._create_output_structure(output_dir)
            
            # Collect all headers from test cases for dynamic config generation
            all_headers = self._extract_headers_from_test_files(test_case_files)
            
            # Generate karate-config.js with dynamic headers
            config = self._create_karate_config(base_url, all_headers)
            config_path = self.repository.save_config(config, functional_dir)
            
            # Extract endpoint summaries from swagger analysis
            endpoint_summaries = self._extract_endpoint_summaries(test_case_files)
            
            # Generate feature for each test case file
            for test_file in test_case_files:
                try:
                    # Load test cases
                    test_data = self.repository.load_test_cases(test_file)
                    
                    # Get endpoint summary
                    endpoint_key = f"{test_data['http_method']}:{test_data['endpoint']}"
                    endpoint_summary = endpoint_summaries.get(endpoint_key)
                    
                    # Convert to KarateFeature with source filename and summary
                    feature = self._convert_to_karate_feature(test_data, test_file.name, endpoint_summary)
                    
                    # Save feature file
                    feature_path = self.repository.save_feature(feature, functional_dir)
                    features_generated.append(str(feature_path))
                    
                    total_scenarios += len(feature.scenarios)
                    total_examples += feature.total_test_cases
                    
                except Exception as e:
                    error_msg = f"Error processing {test_file.name}: {str(e)}"
                    errors.append(error_msg)
            
            success = len(features_generated) > 0
            
            return KarateGenerationResult(
                success=success,
                features_generated=features_generated,
                config_file=str(config_path),
                total_scenarios=total_scenarios,
                total_examples=total_examples,
                errors=errors
            )
        
        except Exception as e:
            return KarateGenerationResult(
                success=False,
                features_generated=features_generated,
                config_file="",
                total_scenarios=total_scenarios,
                total_examples=total_examples,
                errors=[str(e)]
            )
    
    def _create_output_structure(self, output_dir: Path) -> Path:
        """
        Create output directory structure for Karate features.
        
        Args:
            output_dir: Base output directory (e.g., output/functional)
            
        Returns:
            Path to the output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _convert_to_karate_feature(self, test_data: Dict[str, Any], source_filename: str, endpoint_summary: Optional[str] = None) -> KarateFeature:
        """Convert test case data to KarateFeature model."""
        endpoint = test_data["endpoint"]
        http_method = HttpMethod[test_data["http_method"]]
        
        # Extract test cases
        test_cases = test_data.get("test_cases", [])
        success_tests = [tc for tc in test_cases if tc.get("expected_status_code", 0) < 400]
        failure_tests = [tc for tc in test_cases if tc.get("expected_status_code", 0) >= 400]
        
        # Create scenarios
        scenarios = []
        
        # Positive scenario (all success tests)
        if success_tests:
            positive_scenario = self._create_positive_scenario(
                success_tests, 
                http_method, 
                endpoint
            )
            scenarios.append(positive_scenario)
        
        # Negative scenarios grouped by HTTP status
        if failure_tests:
            negative_scenarios = self._create_negative_scenarios(
                failure_tests,
                http_method,
                endpoint
            )
            scenarios.extend(negative_scenarios)
        
        # Use endpoint summary if available, otherwise generate from endpoint
        feature_name = endpoint_summary if endpoint_summary else self._generate_feature_name(endpoint, http_method)
        
        return KarateFeature(
            feature_name=feature_name,
            endpoint=endpoint,
            http_method=http_method,
            scenarios=scenarios,
            source_filename=source_filename,
            total_test_cases=len(test_cases),
            success_count=len(success_tests),
            failure_count=len(failure_tests)
        )
    
    def _create_positive_scenario(
        self,
        test_cases: List[Dict[str, Any]],
        http_method: HttpMethod,
        endpoint: str
    ) -> KarateScenario:
        """Create positive test scenario."""
        examples = []
        
        for tc in test_cases:
            example = KarateExample(
                test_case_id=tc.get("test_case_id", ""),
                test_name=tc.get("test_name", ""),
                test_data=tc.get("test_data", {}),
                expected_status=tc.get("expected_status_code", 200),
                expected_error=None,
                priority=tc.get("priority", "high"),
                tags=tc.get("tags", []),
                partition_category="success"
            )
            examples.append(example)
        
        return KarateScenario(
            name=f"Successful {http_method.value} requests",
            tags=["@smoke", "@positive", f"@{http_method.value.lower()}"],
            scenario_type=ScenarioType.POSITIVE,
            http_method=http_method,
            endpoint=endpoint,
            examples=examples,
            description="Tests with valid inputs that should succeed"
        )
    
    def _create_negative_scenarios(
        self,
        test_cases: List[Dict[str, Any]],
        http_method: HttpMethod,
        endpoint: str
    ) -> List[KarateScenario]:
        """Create negative test scenarios grouped by HTTP status."""
        # Group by status code
        by_status: Dict[int, List[Dict[str, Any]]] = {}
        
        for tc in test_cases:
            status = tc.get("expected_status_code", 400)
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(tc)
        
        scenarios = []
        
        for status, tests in sorted(by_status.items()):
            examples = []
            
            for tc in tests:
                # Extract expected error from test data
                expected_error = self._extract_expected_error(tc)
                
                example = KarateExample(
                    test_case_id=tc.get("test_case_id", ""),
                    test_name=tc.get("test_name", ""),
                    test_data=tc.get("test_data", {}),
                    expected_status=status,
                    expected_error=expected_error,
                    priority=tc.get("priority", "medium"),
                    tags=tc.get("tags", []),
                    partition_category=self._extract_category(tc)
                )
                examples.append(example)
            
            scenario = KarateScenario(
                name=f"{http_method.value} requests returning {status}",
                tags=["@negative", f"@status{status}", f"@{http_method.value.lower()}"],
                scenario_type=ScenarioType.NEGATIVE,
                http_method=http_method,
                endpoint=endpoint,
                examples=examples,
                description=f"Tests that should fail with HTTP {status}"
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _extract_expected_error(self, test_case: Dict[str, Any]) -> Optional[str]:
        """Extract expected error code from test case."""
        # Check in expected_result
        expected_result = test_case.get("expected_result", "")
        if "error" in expected_result.lower():
            # Extract error code pattern like HDR-004, RBV-001
            import re
            match = re.search(r'([A-Z]{3}-\d{3})', expected_result)
            if match:
                return match.group(1)
        
        # Check in partitions_covered
        partitions = test_case.get("partitions_covered", [])
        for partition in partitions:
            constraint_details = partition.get("constraint_details", {})
            error = constraint_details.get("expected_error")
            if error:
                return error
        
        return None
    
    def _extract_category(self, test_case: Dict[str, Any]) -> str:
        """Extract partition category from test case."""
        partitions = test_case.get("partitions_covered", [])
        if partitions:
            return partitions[0].get("category", "validation")
        
        tags = test_case.get("tags", [])
        for tag in tags:
            if tag in ["format", "length", "required", "type"]:
                return tag
        
        return "validation"
    
    def _generate_feature_name(self, endpoint: str, http_method: HttpMethod) -> str:
        """Generate human-readable feature name."""
        # Clean endpoint: /priorities/{id} -> Priorities ID
        parts = [p.replace("{", "").replace("}", "").title() for p in endpoint.split("/") if p]
        resource_name = " ".join(parts)
        return f"{http_method.value} {resource_name}"
    
    def _create_karate_config(self, base_url: str, dynamic_headers: Set[str]) -> KarateConfig:
        """Create Karate configuration using defaults and dynamic environment generation."""
        # Generate environments dynamically based on base_url
        environments = EnvironmentGenerator.generate_environments(base_url)
        
        config = KarateConfig(
            base_url=base_url,
            headers=self.config_defaults.DEFAULT_HEADERS.copy(),
            timeout=self.config_defaults.TIMEOUT_MS,
            retry=self.config_defaults.RETRY_COUNT,
            environments=environments
        )
        
        # Set dynamic headers for config generation
        config.dynamic_headers = dynamic_headers
        
        return config
    
    def _extract_headers_from_test_files(self, test_files: List) -> Set[str]:
        """Extract all unique header names from test case files."""
        all_headers = set()
        
        for test_file in test_files:
            try:
                test_data = self.repository.load_test_cases(test_file)
                
                # Extract headers from test cases
                if "test_cases" in test_data:
                    for test_case in test_data["test_cases"]:
                        if "test_data" in test_case:
                            headers = HeaderExtractor.extract_headers_from_test_data(test_case["test_data"])
                            all_headers.update(headers)
            except Exception:
                # Skip files with errors, will be handled later
                continue
        
        return all_headers
    
    def _extract_base_url_from_test_files(self, test_files: List) -> Optional[str]:
        """
        Extract base URL from test case metadata.
        Looks for source swagger file and reads base_urls from it.
        """
        import json
        
        for test_file in test_files:
            try:
                test_data = self.repository.load_test_cases(test_file)
                
                # Check if metadata contains source_file reference
                if "metadata" in test_data and "source_file" in test_data["metadata"]:
                    swagger_file = Path(test_data["metadata"]["source_file"])
                    
                    if swagger_file.exists():
                        with open(swagger_file, 'r', encoding='utf-8') as f:
                            swagger_data = json.load(f)
                            
                        # Extract base_urls from swagger analysis
                        if "analysis" in swagger_data and "base_urls" in swagger_data["analysis"]:
                            base_urls = swagger_data["analysis"]["base_urls"]
                            if base_urls and len(base_urls) > 0:
                                return base_urls[0]  # Return first base URL
                
            except Exception:
                # Skip files with errors
                continue
        
        return None
    
    def _extract_endpoint_summaries(self, test_files: List) -> Dict[str, str]:
        """
        Extract endpoint summaries from swagger analysis.
        Returns dict with key "METHOD:path" and value "summary".
        """
        import json
        
        summaries = {}
        
        for test_file in test_files:
            try:
                test_data = self.repository.load_test_cases(test_file)
                
                # Check if metadata contains source_file reference
                if "metadata" in test_data and "source_file" in test_data["metadata"]:
                    swagger_file = Path(test_data["metadata"]["source_file"])
                    
                    if swagger_file.exists():
                        with open(swagger_file, 'r', encoding='utf-8') as f:
                            swagger_data = json.load(f)
                        
                        # Extract endpoint summaries
                        if "analysis" in swagger_data and "endpoints" in swagger_data["analysis"]:
                            for endpoint in swagger_data["analysis"]["endpoints"]:
                                method = endpoint.get("method", "")
                                path = endpoint.get("path", "")
                                summary = endpoint.get("summary", "")
                                
                                if method and path and summary:
                                    key = f"{method}:{path}"
                                    summaries[key] = summary
                
            except Exception:
                # Skip files with errors
                continue
        
        return summaries