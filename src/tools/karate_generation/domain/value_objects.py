"""
Value objects for Karate generation domain.
Encapsulates business logic for creating dynamic configurations.
"""
from typing import Dict, Set
from urllib.parse import urlparse


class EnvironmentGenerator:
    """Generates environment configurations dynamically from base URL."""
    
    @staticmethod
    def generate_environments(base_url: str) -> Dict[str, str]:
        """
        Generate environment URLs based on base URL pattern.
        
        Args:
            base_url: Base URL to generate environments from
            
        Returns:
            Dictionary with environment names and URLs
        """
        parsed = urlparse(base_url)
        hostname = parsed.hostname or "localhost"
        port = parsed.port
        scheme = parsed.scheme or "http"
        
        environments = {}
        
        # If localhost, generate standard dev/qa/prod pattern
        if hostname in ["localhost", "127.0.0.1"]:
            port_str = f":{port}" if port else ""
            environments["dev"] = f"{scheme}://localhost{port_str}"
            environments["qa"] = f"{scheme}://qa-api.example.com{port_str}"
            environments["prod"] = f"{scheme}://api.example.com{port_str}"
        else:
            # Extract domain pattern and generate variants
            domain_parts = hostname.split(".")
            
            if len(domain_parts) >= 2:
                # e.g., api.example.com -> dev-api.example.com, qa-api.example.com
                base_domain = ".".join(domain_parts[-2:])
                subdomain = domain_parts[0] if len(domain_parts) > 2 else "api"
                
                environments["dev"] = f"{scheme}://dev-{subdomain}.{base_domain}"
                environments["qa"] = f"{scheme}://qa-{subdomain}.{base_domain}"
                environments["prod"] = f"{scheme}://{subdomain}.{base_domain}"
            else:
                # Simple hostname, use as-is for all environments
                environments["dev"] = base_url
                environments["qa"] = base_url
                environments["prod"] = base_url
        
        return environments


class ValidationCategory:
    """Constants for validation categories."""
    REQUIRED = "required"
    FORMAT = "format"
    TYPE = "type"
    LENGTH = "length"
    VALIDATION = "validation"
    
    @classmethod
    def get_all_categories(cls) -> Set[str]:
        """Get all validation categories."""
        return {cls.REQUIRED, cls.FORMAT, cls.TYPE, cls.LENGTH, cls.VALIDATION}
    
    @classmethod
    def is_header_validation_category(cls, category: str) -> bool:
        """Check if category is related to header validation."""
        return category in {cls.REQUIRED, cls.FORMAT, cls.TYPE, cls.LENGTH}


class HeaderExtractor:
    """Extracts and identifies headers dynamically from test data."""
    
    # Common header patterns to identify
    COMMON_HEADER_PREFIXES = ["x-", "authorization", "content-", "accept"]
    UUID_HEADER_PATTERNS = ["correlation-id", "request-id", "transaction-id", "trace-id", "transaccion-id"]
    UUID_DESCRIPTION_KEYWORDS = ["uuid", "guid", "randomuuid", "unique identifier"]
    
    @staticmethod
    def extract_headers_from_test_data(test_data: Dict) -> Set[str]:
        """
        Extract header names from test case data.
        
        Args:
            test_data: Dictionary with test case data including headers
            
        Returns:
            Set of header names found in test data
        """
        headers = set()
        
        # Check if test_data has header keys using dynamic patterns
        for key in test_data.keys():
            if HeaderExtractor.is_header_field(key):
                headers.add(key)
        
        return headers
    
    @staticmethod
    def is_header_field(field_name: str) -> bool:
        """
        Determine if a field name represents a header.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field represents a header
        """
        field_lower = field_name.lower()
        return any(field_lower.startswith(prefix) for prefix in HeaderExtractor.COMMON_HEADER_PREFIXES)
    
    @staticmethod
    def is_uuid_header(header_name: str, description: str = "") -> bool:
        """
        Check if header typically contains UUID values.
        
        Args:
            header_name: Name of the header
            description: Optional description from swagger to detect UUID hints
            
        Returns:
            True if header typically contains UUIDs
        """
        # Check by header name pattern
        if any(pattern in header_name.lower() for pattern in HeaderExtractor.UUID_HEADER_PATTERNS):
            return True
        
        # Check by description keywords
        if description:
            desc_lower = description.lower()
            return any(keyword in desc_lower for keyword in HeaderExtractor.UUID_DESCRIPTION_KEYWORDS)
        
        return False
    
    @staticmethod
    def extract_header_name_from_field(field_name: str) -> str:
        """
        Extract clean header name from field.
        
        Args:
            field_name: Field name potentially containing header
            
        Returns:
            Normalized header name
        """
        return field_name.lower().strip()
    
    @staticmethod
    def detect_header_hints_in_text(text: str) -> Set[str]:
        """
        Detect header names mentioned in text (e.g., test names).
        
        Args:
            text: Text to search for header mentions
            
        Returns:
            Set of detected header names
        """
        import re
        detected = set()
        
        # Pattern 1: Headers with dashes (x-correlation-id, Transaccion-Id, Aplicacion-Id, etc.)
        # Match word boundaries with Title-Case or lowercase patterns
        dash_pattern = r'\b([A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)*)\b'
        dash_headers = re.findall(dash_pattern, text)
        
        # Filter to only keep likely headers (contain common suffixes or are known patterns)
        header_suffixes = ['-id', '-key', '-token', '-type', '-name', '-consumidor', '-aplicacion', 
                          '-servicio', '-subscription', '-apim', '-api']
        header_prefixes = ['x-', 'ocp-']
        
        for header in dash_headers:
            header_lower = header.lower()
            # Check if it matches header patterns
            is_header = (
                any(header_lower.startswith(prefix) for prefix in header_prefixes) or
                any(header_lower.endswith(suffix) for suffix in header_suffixes) or
                header_lower in ['transaccion-id', 'aplicacion-id', 'nombre-aplicacion',
                                'usuario-consumidor-id', 'nombre-servicio-consumidor',
                                'ocp-apim-subscription-key']
            )
            if is_header:
                detected.add(header)
        
        # Pattern 2: Check for common header keywords
        text_lower = text.lower()
        common_headers = ['authorization', 'content-type', 'accept']
        for header in common_headers:
            if header in text_lower:
                detected.add(header)
        
        return detected
