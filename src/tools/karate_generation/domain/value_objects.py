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


class HeaderExtractor:
    """Extracts and identifies headers dynamically from test data."""
    
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
        
        # Check if test_data has header keys (lowercase with dashes)
        for key in test_data.keys():
            if key.startswith("x-") or key in ["authorization", "content-type", "accept"]:
                headers.add(key)
        
        return headers
    
    @staticmethod
    def is_uuid_header(header_name: str) -> bool:
        """
        Check if header typically contains UUID values.
        
        Args:
            header_name: Name of the header
            
        Returns:
            True if header typically contains UUIDs
        """
        uuid_patterns = ["correlation-id", "request-id", "transaction-id", "trace-id"]
        return any(pattern in header_name.lower() for pattern in uuid_patterns)
