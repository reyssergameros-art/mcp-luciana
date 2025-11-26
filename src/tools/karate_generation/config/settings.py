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
        # Initialize DEFAULT_HEADERS - dynamic headers
        object.__setattr__(self, 'DEFAULT_HEADERS', {
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
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
    
    # Dynamic header names - extracted from test data
    COMMON_HEADER_PATTERNS: list = None
    
    def __post_init__(self):
        # Headers that are commonly used (will be detected dynamically)
        object.__setattr__(self, 'COMMON_HEADER_PATTERNS', [
            'x-correlation-id',
            'x-request-id', 
            'x-transaction-id',
            'authorization',
            'x-api-key'
        ])


# Singleton instances
PATH_CONFIG = KaratePathConfig()
CONFIG_DEFAULTS = KarateConfigDefaults()
FEATURE_CONFIG = FeatureGenerationConfig()
