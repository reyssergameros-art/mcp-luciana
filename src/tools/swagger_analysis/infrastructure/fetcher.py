"""Swagger specification fetcher - handles HTTP and file operations."""
import json
import os
from typing import Dict, Any
import httpx

from ..domain.exceptions import SwaggerFetchError, InvalidUrlError, SpecSizeLimitExceededError
from ....shared.config import settings, SwaggerConstants


class SwaggerFetcher:
    """
    Responsible for fetching swagger specifications from URLs or files.
    
    Follows Single Responsibility Principle - only handles fetching operations.
    """
    
    def __init__(self, timeout: int = None):
        """
        Initialize fetcher with optional timeout.
        
        Args:
            timeout: HTTP request timeout in seconds. Defaults to settings.http_timeout
        """
        self.timeout = timeout or settings.http_timeout
    
    async def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch swagger specification from URL or file path.
        
        Args:
            url: URL or file path to the swagger specification
            
        Returns:
            Parsed swagger specification as dictionary
            
        Raises:
            InvalidUrlError: If URL/path is invalid
            SwaggerFetchError: If fetching fails
            SpecSizeLimitExceededError: If file size exceeds limit
        """
        # Determine if it's a local file or remote URL
        if self._is_local_file(url):
            return await self._fetch_from_file(url)
        elif self._is_remote_url(url):
            return await self._fetch_from_url(url)
        else:
            raise InvalidUrlError(f"Invalid URL or file path: {url}")
    
    def _is_local_file(self, url: str) -> bool:
        """Check if the URL is a local file path."""
        return (
            url.startswith(SwaggerConstants.FILE_PREFIX) or
            (not url.startswith(SwaggerConstants.HTTP_PREFIX) and 
             not url.startswith(SwaggerConstants.HTTPS_PREFIX))
        )
    
    def _is_remote_url(self, url: str) -> bool:
        """Check if the URL is a remote HTTP(S) URL."""
        return (
            url.startswith(SwaggerConstants.HTTP_PREFIX) or 
            url.startswith(SwaggerConstants.HTTPS_PREFIX)
        )
    
    async def _fetch_from_file(self, url: str) -> Dict[str, Any]:
        """
        Fetch swagger spec from local file.
        
        Args:
            url: File path (with or without file:// prefix)
            
        Returns:
            Parsed specification
            
        Raises:
            InvalidUrlError: If file doesn't exist or is not a file
            SwaggerFetchError: If reading or parsing fails
            SpecSizeLimitExceededError: If file size exceeds limit
        """
        try:
            # Remove file:// prefix if present
            file_path = url.replace(SwaggerConstants.FILE_PREFIX, '') if url.startswith(SwaggerConstants.FILE_PREFIX) else url
            
            # Convert to absolute path
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            # Validate file exists
            if not os.path.exists(file_path):
                raise InvalidUrlError(f"File not found: {file_path}")
            
            if not os.path.isfile(file_path):
                raise InvalidUrlError(f"Path is not a file: {file_path}")
            
            # Check file size limit
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > settings.max_spec_size_mb:
                raise SpecSizeLimitExceededError(
                    f"File size ({file_size_mb:.2f}MB) exceeds limit ({settings.max_spec_size_mb}MB)"
                )
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse content
            return self._parse_content(content, file_path)
            
        except (InvalidUrlError, SpecSizeLimitExceededError):
            raise
        except Exception as e:
            raise SwaggerFetchError(f"Failed to read file: {str(e)}") from e
    
    async def _fetch_from_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch swagger spec from remote URL.
        
        Args:
            url: HTTP(S) URL
            
        Returns:
            Parsed specification
            
        Raises:
            SwaggerFetchError: If fetching or parsing fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                
                # Parse based on content type
                if SwaggerConstants.CONTENT_TYPE_JSON in content_type:
                    return response.json()
                elif (SwaggerConstants.CONTENT_TYPE_YAML_APP in content_type or 
                      SwaggerConstants.CONTENT_TYPE_YAML_TEXT in content_type):
                    return self._parse_yaml(response.text)
                else:
                    # Try JSON first, then YAML
                    return self._parse_content(response.text, url)
                    
        except httpx.HTTPStatusError as e:
            raise SwaggerFetchError(
                f"HTTP {e.response.status_code}: Failed to fetch swagger spec"
            ) from e
        except httpx.RequestError as e:
            raise SwaggerFetchError(f"Network error: {str(e)}") from e
        except Exception as e:
            raise SwaggerFetchError(f"Failed to fetch swagger spec: {str(e)}") from e
    
    def _parse_content(self, content: str, source: str) -> Dict[str, Any]:
        """
        Parse content trying JSON first, then YAML.
        
        Args:
            content: String content to parse
            source: Source identifier for logging
            
        Returns:
            Parsed dictionary
            
        Raises:
            SwaggerFetchError: If parsing fails
        """
        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return self._parse_yaml(content)
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """
        Parse YAML content.
        
        Args:
            content: YAML string content
            
        Returns:
            Parsed dictionary
            
        Raises:
            SwaggerFetchError: If YAML parsing fails
        """
        try:
            import yaml
            return yaml.safe_load(content)
        except ImportError:
            raise SwaggerFetchError(
                "YAML parsing requires 'pyyaml' package. Install it with: pip install pyyaml"
            )
        except yaml.YAMLError as e:
            raise SwaggerFetchError(f"Failed to parse YAML content: {str(e)}") from e