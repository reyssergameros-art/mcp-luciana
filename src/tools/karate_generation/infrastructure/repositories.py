"""
Implementation of Karate generation repositories.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from ..domain.repositories import KarateGeneratorRepository
from ..domain.models import KarateFeature, KarateConfig
from ..domain.exceptions import (
    InvalidTestCaseFileError,
    FeatureGenerationError,
    ConfigGenerationError
)
from ..config import PATH_CONFIG
from .feature_builder import KarateFeatureBuilder


class FileKarateRepository(KarateGeneratorRepository):
    """File-based implementation of KarateGeneratorRepository."""
    
    def __init__(self):
        self.feature_builder = KarateFeatureBuilder()
        self.path_config = PATH_CONFIG
    
    def load_test_cases(self, file_path: Path) -> Dict[str, Any]:
        """Load test cases from JSON file."""
        try:
            if not file_path.exists():
                raise InvalidTestCaseFileError(f"File not found: {file_path}")
            
            if not file_path.suffix == ".json":
                raise InvalidTestCaseFileError(f"Invalid file type: {file_path.suffix}. Expected .json")
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if data has metadata structure (new format)
            if "metadata" in data:
                # Transform new format to expected format
                metadata = data.get("metadata", {})
                success_tests = data.get("success_test_cases", [])
                failure_tests = data.get("failure_test_cases", [])
                
                return {
                    "endpoint": metadata.get("endpoint"),
                    "http_method": metadata.get("http_method"),
                    "test_cases": success_tests + failure_tests,
                    "metadata": metadata,
                    "metrics": data.get("metrics", {})
                }
            
            # Validate required fields for old format
            required_fields = ["endpoint", "http_method", "test_cases"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                raise InvalidTestCaseFileError(
                    f"Missing required fields in {file_path.name}: {', '.join(missing_fields)}"
                )
            
            return data
        
        except json.JSONDecodeError as e:
            raise InvalidTestCaseFileError(f"Invalid JSON in file {file_path}: {str(e)}")
        except Exception as e:
            if isinstance(e, InvalidTestCaseFileError):
                raise
            raise InvalidTestCaseFileError(f"Error loading test cases from {file_path}: {str(e)}")
    
    def save_feature(self, feature: KarateFeature, output_dir: Path) -> Path:
        """Save Karate feature to file."""
        try:
            # Create feature directory: output_dir/resources/features/
            features_path = self.path_config.FEATURES_DIR
            feature_dir = output_dir / features_path
            feature_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate file path
            file_path = feature_dir / feature.get_file_name()
            
            # Build feature content
            content = self.feature_builder.build(feature)
            
            # Add generation metadata as comment at the end
            metadata = self._generate_metadata_comment(feature)
            content = f"{content}\n\n{metadata}"
            
            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return file_path
        
        except Exception as e:
            raise FeatureGenerationError(f"Error saving feature {feature.feature_name}: {str(e)}")
    
    def save_config(self, config: KarateConfig, output_dir: Path) -> Path:
        """Save Karate configuration file."""
        try:
            # Create resources directory: output_dir/resources/
            resources_dir = output_dir / "resources"
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            config_path = resources_dir / "karate-config.js"
            content = config.generate_config_content()
            
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return config_path
        
        except Exception as e:
            raise ConfigGenerationError(f"Error saving karate-config.js: {str(e)}")
    
    def list_test_case_files(self, directory: Path) -> List[Path]:
        """List all test case JSON files in directory."""
        if not directory.exists():
            return []
        
        # Find all JSON files in the directory
        json_files = list(directory.glob("*.json"))
        
        # Filter to only test case files
        test_case_files = []
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Check for both old and new format
                    has_old_format = "test_cases" in data and "endpoint" in data
                    has_new_format = "metadata" in data and ("success_test_cases" in data or "failure_test_cases" in data)
                    
                    if has_old_format or has_new_format:
                        test_case_files.append(file_path)
            except (json.JSONDecodeError, IOError):
                # Skip invalid files
                continue
        
        return sorted(test_case_files)
    
    def _generate_metadata_comment(self, feature: KarateFeature) -> str:
        """Generate metadata comment for feature file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# ============================================================
# Feature Generation Metadata
# ============================================================
# Generated: {timestamp}
# Endpoint: {feature.endpoint}
# Method: {feature.http_method.value}
# Total Scenarios: {len(feature.scenarios)}
# Total Test Cases: {feature.total_test_cases}
# Success Cases: {feature.success_count}
# Failure Cases: {feature.failure_count}
# ============================================================"""