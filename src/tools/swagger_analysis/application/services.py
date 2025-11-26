"""Application services for swagger analysis."""
from typing import Dict, Any
from ..domain.repositories import SwaggerRepository
from ..domain.models import SwaggerAnalysisResult
from ..domain.exceptions import SwaggerAnalysisError


class SwaggerAnalysisService:
    """Service for analyzing swagger specifications."""
    
    def __init__(self, repository: SwaggerRepository):
        self._repository = repository
    
    async def analyze_swagger(self, url: str) -> SwaggerAnalysisResult:
        """
        Analyze swagger specification from URL.
        
        Args:
            url: URL to the swagger specification
            
        Returns:
            SwaggerAnalysisResult with detailed analysis
            
        Raises:
            SwaggerAnalysisError: If analysis fails
        """
        try:
            # Fetch the swagger specification
            spec = await self._repository.fetch_swagger_spec(url)
            
            # Parse and analyze the specification
            result = await self._repository.parse_swagger_spec(spec)
            
            return result
        except Exception as e:
            raise
    
    def get_analysis_summary(self, result: SwaggerAnalysisResult) -> Dict[str, Any]:
        """
        Get a summary of the analysis result.
        
        Args:
            result: The swagger analysis result
            
        Returns:
            Dictionary with summary information
        """
        return {
            "title": result.title,
            "version": result.version,
            "description": result.description,
            "base_urls": result.base_urls,
            "total_endpoints": result.total_endpoints,
            "endpoints_by_method": self._count_endpoints_by_method(result),
            "endpoints_with_request_body": self._count_endpoints_with_body(result),
            "response_codes": self._get_unique_response_codes(result)
        }
    
    def convert_field_info_to_dict(self, field_info) -> Dict[str, Any]:
        """
        Convert FieldInfo domain model to dictionary for serialization.
        
        Args:
            field_info: FieldInfo domain model
            
        Returns:
            Dictionary representation
        """
        return {
            "name": field_info.name,
            "data_type": field_info.data_type,
            "required": field_info.required,
            "format": field_info.format.value if hasattr(field_info.format, 'value') else str(field_info.format),
            "description": field_info.description,
            "example": field_info.example,
            "enum_values": field_info.enum_values,
            "pattern": field_info.pattern,
            "minimum": field_info.minimum,
            "maximum": field_info.maximum,
            "min_length": field_info.min_length,
            "max_length": field_info.max_length,
            "constraints": field_info.constraints if field_info.constraints else []
        }
    
    def convert_response_info_to_dict(self, response_info) -> Dict[str, Any]:
        """
        Convert ResponseInfo domain model to dictionary for serialization.
        
        Args:
            response_info: ResponseInfo domain model
            
        Returns:
            Dictionary representation
        """
        return {
            "status_code": response_info.status_code,
            "description": response_info.description,
            "content_type": response_info.content_type,
            "schema": response_info.schema,
            "example": response_info.example,
            "error_codes": response_info.error_codes if response_info.error_codes else [],
            "validation_errors": response_info.validation_errors if response_info.validation_errors else []
        }
    
    def _count_endpoints_by_method(self, result: SwaggerAnalysisResult) -> Dict[str, int]:
        """Count endpoints by HTTP method."""
        method_count = {}
        for endpoint in result.endpoints:
            method = endpoint.method.upper()
            method_count[method] = method_count.get(method, 0) + 1
        return method_count
    
    def _count_endpoints_with_body(self, result: SwaggerAnalysisResult) -> int:
        """Count endpoints that have request body."""
        return sum(1 for endpoint in result.endpoints if endpoint.request_body)
    
    def _get_unique_response_codes(self, result: SwaggerAnalysisResult) -> list:
        """Get unique response codes across all endpoints."""
        codes = set()
        for endpoint in result.endpoints:
            for response in endpoint.responses:
                codes.add(response.status_code)
        return sorted(list(codes))