"""Mappers for converting swagger analysis models to JSON-serializable dictionaries."""
from pathlib import Path
from typing import Dict, Any, List, Optional
from ...tools.swagger_analysis.domain.models import (
    SwaggerAnalysisResult, EndpointInfo, FieldInfo, ResponseInfo
)
from ..utils.file_operations import FileOperations


class SwaggerMapper:
    """Mapper for converting swagger analysis models to dictionaries."""
    
    @staticmethod
    def to_dict(result: SwaggerAnalysisResult) -> Dict[str, Any]:
        """Convert SwaggerAnalysisResult to dictionary."""
        return {
            "title": result.title,
            "version": result.version,
            "description": result.description,
            "contact_info": result.contact_info,
            "license_info": result.license_info,
            "base_urls": result.base_urls,
            "total_endpoints": result.total_endpoints,
            "endpoints": [SwaggerMapper._map_endpoint(ep) for ep in result.endpoints],
            "summary": {
                "title": result.title,
                "version": result.version,
                "description": result.description,
                "base_urls": result.base_urls,
                "total_endpoints": result.total_endpoints,
                "endpoints_by_method": SwaggerMapper._count_by_method(result.endpoints),
                "endpoints_with_request_body": sum(1 for ep in result.endpoints if ep.request_body),
                "response_codes": SwaggerMapper._get_response_codes(result.endpoints)
            }
        }
    
    @staticmethod
    def _map_endpoint(endpoint: EndpointInfo) -> Dict[str, Any]:
        """Map endpoint to dictionary."""
        return {
            "method": endpoint.method,
            "path": endpoint.path,
            "summary": endpoint.summary,
            "description": endpoint.description,
            "operation_id": endpoint.operation_id,
            "tags": endpoint.tags,
            "headers": [SwaggerMapper._map_field(f) for f in endpoint.headers],
            "path_parameters": [SwaggerMapper._map_field(f) for f in endpoint.path_parameters],
            "query_parameters": [SwaggerMapper._map_field(f) for f in endpoint.query_parameters],
            "request_body": {k: SwaggerMapper._map_field(v) for k, v in endpoint.request_body.items()} if endpoint.request_body else None,
            "request_content_type": endpoint.request_content_type,
            "responses": [SwaggerMapper._map_response(r) for r in endpoint.responses],
            "validation_rules": endpoint.validation_rules,
            "error_scenarios": endpoint.error_scenarios
        }
    
    @staticmethod
    def _map_field(field: FieldInfo) -> Dict[str, Any]:
        """Map field to dictionary."""
        constraints = []
        if field.constraints:
            for constraint in field.constraints:
                # Handle ValidationConstraint domain objects properly
                constraints.append({
                    'constraint_type': constraint.constraint_type,
                    'value': constraint.value,
                    'error_code': constraint.error_code,
                    'error_message': constraint.error_message
                })
        
        return {
            "name": field.name,
            "data_type": field.data_type,
            "required": field.required,
            "format": field.format.value if hasattr(field.format, 'value') else str(field.format),
            "description": field.description,
            "example": field.example,
            "enum_values": field.enum_values,
            "pattern": field.pattern,
            "minimum": field.minimum,
            "maximum": field.maximum,
            "min_length": field.min_length,
            "max_length": field.max_length,
            "constraints": constraints
        }
    
    @staticmethod
    def _map_response(response: ResponseInfo) -> Dict[str, Any]:
        """Map response to dictionary."""
        return {
            "status_code": response.status_code,
            "description": response.description,
            "content_type": response.content_type,
            "schema": response.schema,
            "example": response.example,
            "error_codes": response.error_codes if response.error_codes else [],
            "validation_errors": response.validation_errors if response.validation_errors else []
        }
    
    @staticmethod
    def _count_by_method(endpoints: List[EndpointInfo]) -> Dict[str, int]:
        """Count endpoints by HTTP method."""
        counts = {}
        for endpoint in endpoints:
            method = endpoint.method.upper()
            counts[method] = counts.get(method, 0) + 1
        return counts
    
    @staticmethod
    def _get_response_codes(endpoints: List[EndpointInfo]) -> List[str]:
        """Get all unique response codes."""
        codes = set()
        for endpoint in endpoints:
            for response in endpoint.responses:
                codes.add(response.status_code)
        return sorted(list(codes))
    
    @staticmethod
    def _to_camel_case(text: str) -> str:
        """
        Convert text to camelCase.
        
        Args:
            text: Text to convert
            
        Returns:
            Text in camelCase format
        """
        # Remove special characters and split by spaces/underscores
        words = []
        current_word = []
        
        for char in text:
            if char.isalnum():
                current_word.append(char)
            elif current_word:
                words.append(''.join(current_word))
                current_word = []
        
        if current_word:
            words.append(''.join(current_word))
        
        if not words:
            return "swaggerApi"
        
        # Convert to camelCase: first word lowercase, rest capitalized
        camel_case = words[0].lower()
        for word in words[1:]:
            camel_case += word.capitalize()
        
        return camel_case
    
    @staticmethod
    def save_to_json(result_dict: Dict[str, Any], source_url: str) -> Path:
        """
        Save analysis result to JSON file.
        
        Args:
            result_dict: Dictionary with analysis results
            source_url: Source URL or file path being analyzed
            
        Returns:
            Path to the saved JSON file
        """
        # Create output directory
        output_dir = Path("output") / "swagger"
        
        # Extract API name from title or use generic name
        api_name = result_dict.get("title", "swaggerApi")
        # Convert to camelCase
        api_name = SwaggerMapper._to_camel_case(api_name)
        
        filename = f"{api_name}.json"
        file_path = output_dir / filename
        
        # Prepare metadata using FileOperations
        metadata = FileOperations.create_metadata(
            source=source_url,
            technique="Swagger Analysis"
        )
        
        output_data = {
            "metadata": metadata,
            "analysis": result_dict
        }
        
        # Use FileOperations to save JSON
        return FileOperations.save_json(output_data, file_path)