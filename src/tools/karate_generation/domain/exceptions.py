"""
Custom exceptions for Karate generation domain.
"""


class KarateGenerationError(Exception):
    """Base exception for Karate generation errors."""
    pass


class InvalidTestCaseFileError(KarateGenerationError):
    """Raised when test case JSON file is invalid or malformed."""
    pass


class FeatureGenerationError(KarateGenerationError):
    """Raised when feature file generation fails."""
    pass


class ConfigGenerationError(KarateGenerationError):
    """Raised when config file generation fails."""
    pass


class InvalidEndpointError(KarateGenerationError):
    """Raised when endpoint format is invalid."""
    pass