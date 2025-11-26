"""
Repository interfaces for Karate generation domain.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

from .models import KarateFeature, KarateConfig


class KarateGeneratorRepository(ABC):
    """Repository interface for generating Karate features."""
    
    @abstractmethod
    def load_test_cases(self, file_path: Path) -> Dict[str, Any]:
        """
        Load test cases from JSON file.
        
        Args:
            file_path: Path to the test cases JSON file
            
        Returns:
            Dictionary with test case data
            
        Raises:
            InvalidTestCaseFileError: If file is invalid or malformed
        """
        pass
    
    @abstractmethod
    def save_feature(self, feature: KarateFeature, output_dir: Path) -> Path:
        """
        Save Karate feature to file.
        
        Args:
            feature: KarateFeature to save
            output_dir: Output directory path
            
        Returns:
            Path to the saved feature file
            
        Raises:
            FeatureGenerationError: If feature cannot be saved
        """
        pass
    
    @abstractmethod
    def save_config(self, config: KarateConfig, output_dir: Path) -> Path:
        """
        Save Karate configuration file.
        
        Args:
            config: KarateConfig to save
            output_dir: Output directory path
            
        Returns:
            Path to the saved config file
            
        Raises:
            ConfigGenerationError: If config cannot be saved
        """
        pass
    
    @abstractmethod
    def list_test_case_files(self, directory: Path) -> List[Path]:
        """
        List all test case JSON files in directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of Path objects for test case files
        """
        pass