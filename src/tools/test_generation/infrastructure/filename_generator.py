"""Filename generator for test case JSON files following camelCase convention."""
from typing import Dict


class FilenameGenerator:
    """
    Generates camelCase filenames for test case JSON files.
    
    Naming Convention:
    - Lowercase HTTP method + PascalCase path
    - Example: postBeneficiarios.json, getBeneficiariosId.json, putPrioritiesId.json
    
    Principles:
    - Single Responsibility: Only generates filenames
    - Open/Closed: Easy to extend with new naming strategies
    """
    
    # Mapping of common path segments to camelCase
    COMMON_WORDS = {
        "id": "Id",
        "api": "Api",
        "url": "Url",
        "uuid": "Uuid",
        "uri": "Uri"
    }
    
    def generate(self, http_method: str, endpoint: str) -> str:
        """
        Generate camelCase filename from HTTP method and endpoint.
        
        Rules:
        - HTTP method in lowercase (get, post, put, delete, patch)
        - Path segments converted to PascalCase (all capitalized)
        - Remove slashes, curly braces, hyphens
        - Special words (id, api) properly capitalized
        
        Args:
            http_method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint path (/beneficiarios/{id}, /priorities)
            
        Returns:
            camelCase filename without extension
            
        Examples:
            >>> gen = FilenameGenerator()
            >>> gen.generate("POST", "/beneficiarios")
            'postBeneficiarios'
            >>> gen.generate("GET", "/beneficiarios/{id}")
            'getBeneficiariosId'
            >>> gen.generate("PUT", "/priorities/{id}")
            'putPrioritiesId'
            >>> gen.generate("DELETE", "/api-resources")
            'deleteApiResources'
        """
        # Lowercase method
        method_lower = http_method.lower()
        
        # Clean and split endpoint
        path_cleaned = self._clean_path(endpoint)
        path_segments = self._split_path(path_cleaned)
        
        # Convert to camelCase
        camel_case = self._to_camel_case(path_segments)
        
        # Combine method + camelCase path
        filename = f"{method_lower}{camel_case}"
        
        return filename
    
    def _clean_path(self, path: str) -> str:
        """
        Clean path by removing special characters.
        
        Args:
            path: Original endpoint path
            
        Returns:
            Cleaned path with only alphanumeric and separators
        """
        # Remove leading/trailing slashes
        cleaned = path.strip("/")
        
        # Remove curly braces (parameter markers)
        cleaned = cleaned.replace("{", "").replace("}", "")
        
        return cleaned
    
    def _split_path(self, path: str) -> list[str]:
        """
        Split path into segments using multiple separators.
        
        Handles:
        - Forward slashes: /api/users → ['api', 'users']
        - Hyphens: api-resources → ['api', 'resources']
        - Underscores: user_profile → ['user', 'profile']
        
        Args:
            path: Cleaned path string
            
        Returns:
            List of path segments
        """
        # Replace hyphens and underscores with slashes for uniform splitting
        path = path.replace("-", "/").replace("_", "/")
        
        # Split by slashes and filter empty strings
        segments = [s for s in path.split("/") if s]
        
        return segments
    
    def _to_camel_case(self, segments: list[str]) -> str:
        """
        Convert list of segments to PascalCase (all segments capitalized).
        
        Rules:
        - All segments: capitalize first letter (PascalCase for path)
        - Special words get proper casing (id → Id, api → Api)
        - Method will be lowercase, path will be PascalCase
        
        Args:
            segments: List of path segments
            
        Returns:
            PascalCase string
            
        Examples:
            ['beneficiarios', 'id'] → 'BeneficiariosId'
            ['priorities', 'id'] → 'PrioritiesId'
            ['api', 'resources'] → 'ApiResources'
        """
        if not segments:
            return ""
        
        camel_parts = []
        
        for segment in segments:
            segment_lower = segment.lower()
            
            # Check if it's a special word
            if segment_lower in self.COMMON_WORDS:
                # Special word: use predefined casing
                camel_parts.append(self.COMMON_WORDS[segment_lower])
            else:
                # Regular word: capitalize first letter (PascalCase)
                camel_parts.append(segment.capitalize())
        
        return "".join(camel_parts)
