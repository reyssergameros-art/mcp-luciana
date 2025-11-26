"""Schema resolver for handling $ref references in swagger specifications."""
from typing import Dict, Any, Optional

from ..domain.exceptions import SwaggerParseError
from ....shared.config import SwaggerConstants


class SchemaResolver:
    """
    Responsible for resolving $ref references in swagger specifications.
    
    Follows Single Responsibility Principle - only handles reference resolution.
    """
    
    def __init__(self, spec: Dict[str, Any]):
        """
        Initialize resolver with the full specification.
        
        Args:
            spec: Complete swagger/OpenAPI specification
        """
        self.spec = spec
        self._resolution_stack = []  # Track resolution path to detect circular refs
    
    def resolve(self, ref: str) -> Dict[str, Any]:
        """
        Resolve a $ref reference.
        
        Args:
            ref: Reference string (e.g., "#/components/schemas/User")
            
        Returns:
            Resolved schema dictionary
            
        Raises:
            SwaggerParseError: If reference cannot be resolved or is circular
        """
        if not ref:
            return {}
        
        if not ref.startswith('#/'):
            return {}
        
        # Check for circular references
        if ref in self._resolution_stack:
            raise SwaggerParseError(
                f"Circular reference detected: {' -> '.join(self._resolution_stack + [ref])}"
            )
        
        self._resolution_stack.append(ref)
        
        try:
            result = self._resolve_internal_ref(ref)
            return result
        finally:
            self._resolution_stack.pop()
    
    def _resolve_internal_ref(self, ref: str) -> Dict[str, Any]:
        """
        Resolve internal reference within the same document.
        
        Args:
            ref: Internal reference starting with #/
            
        Returns:
            Resolved schema dictionary
            
        Raises:
            SwaggerParseError: If path is invalid
        """
        # Remove #/ prefix and split path
        path_parts = ref[2:].split('/')
        current = self.spec
        
        try:
            for part in path_parts:
                # Handle URL-encoded characters in path parts
                part = part.replace('1', '/').replace('~0', '')
                current = current[part]
            
            return current
            
        except (KeyError, TypeError) as e:
            raise SwaggerParseError(
                f"Cannot resolve reference '{ref}': path not found in specification"
            ) from e
    
    def resolve_if_ref(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve schema if it contains a $ref, otherwise return as-is.
        
        Args:
            schema: Schema dictionary that may contain $ref
            
        Returns:
            Resolved schema or original schema
        """
        if not isinstance(schema, dict):
            return schema
        
        if SwaggerConstants.FIELD_REF in schema:
            return self.resolve(schema[SwaggerConstants.FIELD_REF])
        
        return schema
    
    def resolve_schema_recursively(self, schema: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """
        Recursively resolve all $ref references in a schema.
        
        Args:
            schema: Schema dictionary
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            Fully resolved schema
            
        Raises:
            SwaggerParseError: If max depth exceeded
        """
        if max_depth <= 0:
            raise SwaggerParseError("Maximum schema resolution depth exceeded")
        
        if not isinstance(schema, dict):
            return schema
        
        # Resolve current level if it's a ref
        if SwaggerConstants.FIELD_REF in schema:
            schema = self.resolve(schema[SwaggerConstants.FIELD_REF])
        
        # Recursively resolve nested schemas
        resolved = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve_schema_recursively(value, max_depth - 1)
            elif isinstance(value, list):
                resolved[key] = [
                    self.resolve_schema_recursively(item, max_depth - 1) 
                    if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                resolved[key] = value
        
        return resolved