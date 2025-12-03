"""
Configuration settings for Karate generation.
Centralizes all configuration to avoid hardcoded values.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class KaratePathConfig:
    """Configuration for Karate output paths."""
    
    # Base output directory
    OUTPUT_BASE: str = "output/functional"
    
    # Feature files directory
    FEATURES_DIR: str = "resources/features"
    
    # Configuration file
    CONFIG_FILE: str = "resources/karate-config.js"
    
    def get_features_path(self) -> str:
        """Get full path to features directory."""
        return f"{self.OUTPUT_BASE}/{self.FEATURES_DIR}"
    
    def get_config_path(self) -> str:
        """Get full path to config file."""
        return f"{self.OUTPUT_BASE}/{self.CONFIG_FILE}"


@dataclass(frozen=True)
class KarateConfigDefaults:
    """Default values for Karate configuration."""
    
    # Default timeout in milliseconds
    TIMEOUT_MS: int = 30000
    
    # Default retry count
    RETRY_COUNT: int = 0
    
    def __post_init__(self):
        # Initialize DEFAULT_HEADERS - will be populated from swagger content-type/accept
        object.__setattr__(self, 'DEFAULT_HEADERS', {})
        
        # Initialize ENVIRONMENTS - will be populated dynamically from base_url
        object.__setattr__(self, 'ENVIRONMENTS', {})


@dataclass(frozen=True)
class FeatureGenerationConfig:
    """Configuration for feature file generation."""
    
    # Gherkin indentation
    INDENT_SPACES: int = 2
    
    # Tags for scenarios
    REGRESSION_TAG: str = "@regression"
    SMOKE_TAG: str = "@smoke"
    NEGATIVE_TAG: str = "@negative"
    POSITIVE_TAG: str = "@positive"
    
    # Scenario grouping
    GROUP_BY_STATUS: bool = True
    
    # File naming
    FILE_EXTENSION: str = ".feature"
    
    # Header validation actions
    HEADER_VALIDATION_ACTIONS: dict = None
    
    # Validation condition mappings
    VALIDATION_CONDITIONS: dict = None
    
    def __post_init__(self):
        # Actions for different validation types
        object.__setattr__(self, 'HEADER_VALIDATION_ACTIONS', {
            'required_null': {'action': 'null', 'keywords': ['null', 'nulo']},
            'required_missing': {'action': 'remove', 'keywords': []},
            'format': {'action': 'null', 'condition_suffix': 'formato'},
            'type': {'action': 'null', 'condition_suffix': 'tipo'},
            'length': {'action': 'null', 'condition_suffix': 'longitud'},
            'default': {'action': 'remove', 'condition': 'es inválido'}
        })
        
        # Condition templates for validation scenarios
        object.__setattr__(self, 'VALIDATION_CONDITIONS', {
            'required_null': 'tiene valor nulo',
            'required_missing': 'no está presente',
            'format': 'tiene valor inválido (formato)',
            'type': 'tiene valor inválido (tipo)',
            'length': 'tiene valor inválido (longitud)',
            'default': 'es inválido'
        })


# Singleton instances
PATH_CONFIG = KaratePathConfig()
CONFIG_DEFAULTS = KarateConfigDefaults()
FEATURE_CONFIG = FeatureGenerationConfig()
