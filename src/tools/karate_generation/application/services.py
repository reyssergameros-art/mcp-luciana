"""
Application services for Karate feature generation.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

logger = logging.getLogger(__name__)

from ..domain.models import (
    KarateFeature,
    KarateScenario,
    KarateExample,
    KarateConfig,
    KarateGenerationResult,
    ScenarioType,
    HttpMethod
)
# Import at module level for status description mapping
_get_http_status_description = KarateExample.get_http_status_description
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
        
        # Generate descriptive scenario name
        action_verb = self._get_action_verb_for_method(http_method)
        resource_name = self._extract_resource_name(endpoint)
        
        return KarateScenario(
            name=f"{action_verb} {resource_name} exitosamente",
            tags=[],  # Tags generated dynamically by get_all_tags()
            scenario_type=ScenarioType.POSITIVE,
            http_method=http_method,
            endpoint=endpoint,
            examples=examples,
            description=f"Caso exitoso: {action_verb.lower()} con parámetros válidos"
        )
    
    def _create_negative_scenarios(
        self,
        test_cases: List[Dict[str, Any]],
        http_method: HttpMethod,
        endpoint: str
    ) -> List[KarateScenario]:
        """Create negative test scenarios grouped by HTTP status code with specific descriptions."""
        # Group by status code first
        by_status: Dict[int, List[Dict[str, Any]]] = {}
        
        for tc in test_cases:
            status = tc.get("expected_status_code", 400)
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(tc)
        
        scenarios = []
        
        for status, tests in sorted(by_status.items()):
            # Further group by header validation type
            header_tests, other_tests = self._separate_header_tests(tests)
            
            # Create scenarios for header validation tests (grouped by header name)
            if header_tests:
                header_scenarios = self._create_header_validation_scenarios(
                    header_tests, http_method, endpoint, status
                )
                scenarios.extend(header_scenarios)
            
            # Create scenario for other tests with specific status code descriptions
            if other_tests:
                examples = []
                
                for tc in other_tests:
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
                
                # Get specific status code description
                status_desc = _get_http_status_description(status)
                
                # Create more descriptive scenario names based on status code
                scenario_name = self._generate_scenario_name_for_status(
                    status, status_desc, http_method, endpoint
                )
                
                scenario = KarateScenario(
                    name=scenario_name,
                    tags=["@negativeTest", f"@{http_method.value.lower()}", f"@status{status}"],
                    scenario_type=ScenarioType.NEGATIVE,
                    http_method=http_method,
                    endpoint=endpoint,
                    examples=examples,
                    description=f"Tests que deben retornar {status_desc} ({status})"
                )
                scenarios.append(scenario)
        
        return scenarios
    
    def _generate_scenario_name_for_status(
        self, 
        status: int, 
        status_desc: str, 
        http_method: HttpMethod, 
        endpoint: str
    ) -> str:
        """Generate descriptive scenario name based on status code."""
        
        # Specific descriptions for common status codes (more concise and action-oriented)
        status_scenarios = {
            400: "Rechazar solicitud con datos inválidos",
            401: "Rechazar solicitud sin autenticación",
            403: "Rechazar solicitud sin permisos suficientes",
            404: "Rechazar solicitud de recurso inexistente",
            405: "Rechazar solicitud con método HTTP no permitido",
            409: "Rechazar solicitud por conflicto de recursos",
            422: "Rechazar solicitud con datos no procesables",
            429: "Rechazar solicitud por exceso de llamadas",
            500: "Manejar error interno del servidor",
            502: "Manejar error de gateway inválido",
            503: "Manejar servicio no disponible",
            504: "Manejar timeout del gateway"
        }
        
        # Return specific scenario name or generic one
        return status_scenarios.get(
            status,
            f"Verificar respuesta {status_desc} ({status})"
        )
    
    def _separate_header_tests(self, test_cases: List[Dict[str, Any]]) -> tuple:
        """Separate header validation tests from other tests."""
        from ..domain.value_objects import ValidationCategory, HeaderExtractor
        
        header_tests = []
        other_tests = []
        
        for tc in test_cases:
            test_name = tc.get("test_name", "")
            category = self._extract_category(tc)
            
            # Check if it's a header validation test using dynamic detection
            is_header_category = ValidationCategory.is_header_validation_category(category)
            has_header_hints = len(HeaderExtractor.detect_header_hints_in_text(test_name)) > 0
            
            if is_header_category and has_header_hints:
                header_tests.append(tc)
            else:
                other_tests.append(tc)
        
        return header_tests, other_tests
    
    def _create_header_validation_scenarios(
        self,
        test_cases: List[Dict[str, Any]],
        http_method: HttpMethod,
        endpoint: str,
        status: int
    ) -> List[KarateScenario]:
        """Create scenarios for header validation tests, grouped by header name and validation type."""
        # Group by header name first
        by_header: Dict[str, List[Dict[str, Any]]] = {}
        
        for tc in test_cases:
            header_name = self._extract_header_name_from_test(tc)
            if header_name not in by_header:
                by_header[header_name] = []
            by_header[header_name].append(tc)
        
        scenarios = []
        
        for header_name, tests in by_header.items():
            # Further separate by validation type: required (missing/empty) vs type (invalid value)
            required_tests = []
            type_tests = []
            
            for tc in tests:
                test_data = tc.get("test_data", {})
                # If header has a non-empty value, it's type validation
                header_value = test_data.get(header_name)
                if header_value not in [None, "", [], {}]:
                    type_tests.append(tc)
                else:
                    required_tests.append(tc)
            
            # Create scenario for required validation (missing/empty header)
            if required_tests:
                examples = []
                for tc in required_tests:
                    header_validation = self._create_header_validation_metadata(tc, header_name)
                    expected_error = self._extract_expected_error(tc)
                    
                    example = KarateExample(
                        test_case_id=tc.get("test_case_id", ""),
                        test_name=tc.get("test_name", ""),
                        test_data=tc.get("test_data", {}),
                        expected_status=status,
                        expected_error=expected_error,
                        priority=tc.get("priority", "medium"),
                        tags=tc.get("tags", []),
                        partition_category=self._extract_category(tc),
                        header_validation=header_validation
                    )
                    examples.append(example)
                
                scenario = KarateScenario(
                    name=f"Rechazar solicitud cuando falta header requerido",
                    tags=["@error", "@validation", f"@{http_method.value.lower()}"],
                    scenario_type=ScenarioType.NEGATIVE,
                    http_method=http_method,
                    endpoint=endpoint,
                    examples=examples,
                    description=f"Tests para validar {header_name} requerido"
                )
                scenarios.append(scenario)
            
            # Create scenario for type validation (invalid value)
            if type_tests:
                examples = []
                for tc in type_tests:
                    header_validation = self._create_header_validation_metadata(tc, header_name)
                    expected_error = self._extract_expected_error(tc)
                    
                    example = KarateExample(
                        test_case_id=tc.get("test_case_id", ""),
                        test_name=tc.get("test_name", ""),
                        test_data=tc.get("test_data", {}),
                        expected_status=status,
                        expected_error=expected_error,
                        priority=tc.get("priority", "medium"),
                        tags=tc.get("tags", []),
                        partition_category=self._extract_category(tc),
                        header_validation=header_validation
                    )
                    examples.append(example)
                
                scenario = KarateScenario(
                    name=f"Rechazar solicitud cuando header tiene tipo incorrecto",
                    tags=["@error", "@validation", "@invalid-type", f"@{http_method.value.lower()}"],
                    scenario_type=ScenarioType.NEGATIVE,
                    http_method=http_method,
                    endpoint=endpoint,
                    examples=examples,
                    description=f"Tests para validar tipo de {header_name}"
                )
                scenarios.append(scenario)
        
        return scenarios
    
    def _extract_header_name_from_test(self, test_case: Dict[str, Any]) -> str:
        """Extract header name being tested from test case."""
        from ..domain.value_objects import HeaderExtractor
        
        test_name = test_case.get("test_name", "")
        
        # Try to extract from test_name using dynamic detection
        detected_headers = HeaderExtractor.detect_header_hints_in_text(test_name)
        if detected_headers:
            return list(detected_headers)[0]
        
        # Check partitions_covered
        partitions = test_case.get("partitions_covered", [])
        for partition in partitions:
            field_name = partition.get("field_name", "")
            if HeaderExtractor.is_header_field(field_name):
                return HeaderExtractor.extract_header_name_from_field(field_name)
        
        return "unknown-header"
    
    def _create_header_validation_metadata(self, test_case: Dict[str, Any], header_name: str) -> Dict[str, str]:
        """Create header validation metadata for scenario outline."""
        from ..config import FEATURE_CONFIG
        from ..domain.value_objects import ValidationCategory
        
        category = self._extract_category(test_case)
        test_name = test_case.get("test_name", "").lower()
        
        # Use dynamic configuration for actions and conditions
        action_config = FEATURE_CONFIG.HEADER_VALIDATION_ACTIONS
        condition_config = FEATURE_CONFIG.VALIDATION_CONDITIONS
        
        # Determine action and condition based on category
        if category == ValidationCategory.REQUIRED:
            # Check for null keywords
            has_null_keyword = any(keyword in test_name for keyword in action_config['required_null']['keywords'])
            if has_null_keyword:
                action = action_config['required_null']['action']
                condition = condition_config['required_null']
            else:
                action = action_config['required_missing']['action']
                condition = condition_config['required_missing']
        elif category in [ValidationCategory.FORMAT, ValidationCategory.TYPE, ValidationCategory.LENGTH]:
            # For format/type/length errors
            action = action_config.get(category, action_config['default'])['action']
            condition = condition_config.get(category, condition_config['default'])
        else:
            # Default case
            action = action_config['default']['action']
            condition = action_config['default'].get('condition', condition_config['default'])
        
        return {
            "headerName": header_name,
            "condition": condition,
            "action": action
        }
    
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
        from ..domain.value_objects import ValidationCategory
        
        # Try from partitions_covered first
        partitions = test_case.get("partitions_covered", [])
        if partitions:
            category = partitions[0].get("category", ValidationCategory.VALIDATION)
            return category
        
        # Try from tags
        tags = test_case.get("tags", [])
        all_categories = ValidationCategory.get_all_categories()
        for tag in tags:
            if tag in all_categories:
                return tag
        
        return ValidationCategory.VALIDATION
    
    def _generate_feature_name(self, endpoint: str, http_method: HttpMethod) -> str:
        """Generate human-readable feature name."""
        # Clean endpoint: /priorities/{id} -> Priorities ID
        parts = [p.replace("{", "").replace("}", "").title() for p in endpoint.split("/") if p]
        resource_name = " ".join(parts)
        return f"{http_method.value} {resource_name}"
    
    def _get_action_verb_for_method(self, http_method: HttpMethod) -> str:
        """Get Spanish action verb for HTTP method."""
        verb_map = {
            HttpMethod.GET: "Obtener",
            HttpMethod.POST: "Crear",
            HttpMethod.PUT: "Actualizar",
            HttpMethod.PATCH: "Modificar",
            HttpMethod.DELETE: "Eliminar"
        }
        return verb_map.get(http_method, http_method.value)
    
    def _extract_resource_name(self, endpoint: str) -> str:
        """Extract resource name from endpoint path."""
        # /polizas/{numeroPoliza}/descargar -> "documento de póliza"
        # /priorities -> "prioridad"
        # /users/{id} -> "usuario"
        parts = [p for p in endpoint.split("/") if p and not p.startswith("{")]
        
        if not parts:
            return "recurso"
        
        # Use the first meaningful part
        resource = parts[0].replace("-", " ").replace("_", " ")
        
        # If there's an action at the end (descargar, download, etc.)
        if len(parts) > 1 and parts[-1] in ["descargar", "download", "upload", "search"]:
            action_map = {
                "descargar": "descarga",
                "download": "download",
                "upload": "carga",
                "search": "búsqueda"
            }
            return f"{action_map.get(parts[-1], parts[-1])} de {resource}"
        
        return resource
    
    def _create_karate_config(self, base_url: str, dynamic_headers: Dict[str, Dict[str, Any]]) -> KarateConfig:
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
        
        # Set dynamic headers with metadata for config generation
        config.dynamic_headers = dynamic_headers
        
        return config
    
    def _extract_headers_from_test_files(self, test_files: List) -> Dict[str, Dict[str, Any]]:
        """Extract all unique headers with metadata from swagger analysis.
        
        Returns:
            Dict with header_name as key and dict with 'description', 'required', 'type' as value
        """
        all_headers = {}
        content_types = set()
        accept_types = set()
        
        for test_file in test_files:
            try:
                test_data = self.repository.load_test_cases(test_file)
                
                # Extract headers from swagger analysis source
                if "metadata" in test_data and "source_file" in test_data["metadata"]:
                    swagger_file = Path(test_data["metadata"]["source_file"])
                    
                    if swagger_file.exists():
                        with open(swagger_file, 'r', encoding='utf-8') as f:
                            swagger_data = json.load(f)
                        
                        # Extract headers and content-types from endpoints
                        if "analysis" in swagger_data and "endpoints" in swagger_data["analysis"]:
                            for endpoint in swagger_data["analysis"]["endpoints"]:
                                # Extract custom headers
                                if "headers" in endpoint:
                                    for header in endpoint["headers"]:
                                        header_name = header.get("name")
                                        if header_name:
                                            all_headers[header_name] = {
                                                "description": header.get("description", ""),
                                                "required": header.get("required", False),
                                                "type": header.get("data_type", "string")
                                            }
                                
                                # Extract Content-Type from request_content_type
                                if endpoint.get("request_content_type"):
                                    content_types.add(endpoint["request_content_type"])
                                
                                # Extract Accept from response content_types
                                if "responses" in endpoint:
                                    for response in endpoint["responses"]:
                                        if response.get("content_type"):
                                            accept_types.add(response["content_type"])
                
                # Fallback: extract from test_data if swagger not available
                if not all_headers and "test_cases" in test_data:
                    for test_case in test_data["test_cases"]:
                        if "test_data" in test_case:
                            headers = HeaderExtractor.extract_headers_from_test_data(test_case["test_data"])
                            for header in headers:
                                all_headers[header] = {
                                    "description": "",
                                    "required": False,
                                    "type": "string"
                                }
            except Exception:
                # Skip files with errors, will be handled later
                continue
        
        # Add Content-Type header if found in swagger
        if content_types:
            all_headers["Content-Type"] = {
                "description": "Media type of the request body",
                "required": True,
                "type": "string",
                "value": list(content_types)[0]  # Use first found content type
            }
        
        # Add Accept header if found in swagger
        if accept_types:
            all_headers["Accept"] = {
                "description": "Media type(s) that the client can understand",
                "required": True,
                "type": "string",
                "value": list(accept_types)[0]  # Use first found accept type
            }
        
        return all_headers
    
    def _extract_base_url_from_test_files(self, test_files: List) -> Optional[str]:
        """
        Extract base URL from test case metadata.
        Looks for source swagger file and reads base_urls from it.
        """
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