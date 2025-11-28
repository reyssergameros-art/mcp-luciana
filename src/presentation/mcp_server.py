"""
MCP Server for Swagger Analysis Tool using FastMCP.
"""

from pathlib import Path
from fastmcp import FastMCP
from pydantic import BaseModel, field_validator
from typing import Optional

from src.tools.mcp_tools import MCPToolsOrchestrator


class SwaggerAnalysisRequest(BaseModel):
    """Request model for Swagger analysis"""
    swagger_url: str
    format: Optional[str] = "detailed"  # "detailed" or "summary"
    save_output: Optional[bool] = True  # Save to JSON file
    output_format: Optional[str] = "both"  # "console", "file", or "both"
    
    @field_validator('swagger_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is either a valid HTTP(S) URL or an existing file path."""
        if v.startswith('http://') or v.startswith('https://'):
            return v
        
        # Check if it's a file path (with or without file:// prefix)
        file_path = v.replace('file://', '') if v.startswith('file://') else v
        path = Path(file_path)
        
        if not path.is_absolute():
            path = Path.cwd() / file_path
        
        if not path.exists():
            raise ValueError(f"File path does not exist: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        return v
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v: Optional[str]) -> str:
        """Validate format is either 'detailed' or 'summary'."""
        if v not in ['detailed', 'summary']:
            raise ValueError("Format must be 'detailed' or 'summary'")
        return v
    
    @field_validator('output_format')
    @classmethod
    def validate_output_format(cls, v: Optional[str]) -> str:
        """Validate output_format is 'console', 'file', or 'both'."""
        if v not in ['console', 'file', 'both']:
            raise ValueError("output_format must be 'console', 'file', or 'both'")
        return v


class TestGenerationRequest(BaseModel):
    """Request model for test case generation (supports multiple ISTQB v4 techniques)"""
    swagger_analysis_file: str
    technique: Optional[str] = "equivalence_partitioning"  # "equivalence_partitioning" or "boundary_value_analysis"
    bva_version: Optional[str] = "2-value"  # Only for BVA: "2-value" or "3-value"
    endpoint_filter: Optional[str] = None
    method_filter: Optional[str] = None
    save_output: Optional[bool] = True
    
    @field_validator('swagger_analysis_file')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate that file path exists."""
        path = Path(v)
        
        if not path.is_absolute():
            path = Path.cwd() / v
        
        if not path.exists():
            raise ValueError(f"File not found: {v}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {v}")
        
        if not path.suffix == '.json':
            raise ValueError(f"File must be JSON format: {v}")
        
        return str(path)
    
    @field_validator('technique')
    @classmethod
    def validate_technique(cls, v: Optional[str]) -> str:
        """Validate testing technique."""
        if v not in ['equivalence_partitioning', 'boundary_value_analysis']:
            raise ValueError("Technique must be 'equivalence_partitioning' or 'boundary_value_analysis'")
        return v
    
    @field_validator('bva_version')
    @classmethod
    def validate_bva_version(cls, v: Optional[str]) -> str:
        """Validate BVA version."""
        if v not in ['2-value', '3-value']:
            raise ValueError("BVA version must be '2-value' or '3-value'")
        return v
    
    @field_validator('method_filter')
    @classmethod
    def validate_method(cls, v: Optional[str]) -> Optional[str]:
        """Validate HTTP method if provided."""
        if v is None:
            return v
        
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if v.upper() not in valid_methods:
            raise ValueError(f"Invalid HTTP method. Must be one of: {', '.join(valid_methods)}")
        
        return v.upper()


class KarateGenerationRequest(BaseModel):
    """Request model for Karate feature generation"""
    test_cases_directory: str
    base_url: Optional[str] = "http://localhost:8080"
    output_directory: Optional[str] = None
    
    @field_validator('test_cases_directory')
    @classmethod
    def validate_directory(cls, v: str) -> str:
        """Validate that directory exists."""
        path = Path(v)
        
        if not path.is_absolute():
            path = Path.cwd() / v
        
        if not path.exists():
            raise ValueError(f"Directory not found: {v}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        
        return str(path)
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> str:
        """Validate base URL format."""
        if not v:
            return "http://localhost:8080"
        
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("base_url must start with http:// or https://")
        
        return v


class SwaggerAnalysisMCPServer:
    """MCP Server for Swagger Analysis Tool"""
    
    def __init__(self):
        self.mcp = FastMCP("MCP-Swagger-Analysis")
        self.orchestrator = MCPToolsOrchestrator()
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools"""
        
        @self.mcp.tool()
        async def swagger_analysis(request: SwaggerAnalysisRequest) -> str:
            """
            Analyze Swagger/OpenAPI specifications from URL or file path.

            This tool provides comprehensive analysis of Swagger/OpenAPI specifications:
            - API structure and endpoints discovery
            - HTTP methods for each endpoint
            - Request headers (required/optional, types, constraints)
            - Request body structure and validation rules
            - Response definitions with status codes and descriptions
            - Automatic error handling and validation

            Args:
                request: SwaggerAnalysisRequest with swagger_url and format

            Returns:
                Complete analysis report in JSON format
            """
            try:
                result = await self.orchestrator.analyze_swagger_from_url(
                    swagger_url=request.swagger_url,
                    save_output=request.save_output,
                    output_format=request.output_format
                )
                
                import json
                return json.dumps(result, indent=2)
            except Exception as e:
                raise
        
        @self.mcp.tool()
        async def generate_test_cases(request: TestGenerationRequest) -> str:
            """
            Generate test cases using ISTQB v4 testing techniques.
            
            Supports multiple testing techniques:
            
            **Equivalence Partitioning (technique="equivalence_partitioning")**:
            - Identifies valid and invalid equivalence partitions
            - Creates positive tests (all valid inputs)
            - Creates negative tests (one invalid input at a time)
            - Achieves 100% partition coverage (ISTQB requirement)
            - Based on ISTQB v4: "Divides data into partitions where all elements 
              should be processed the same way"
            
            **Boundary Value Analysis (technique="boundary_value_analysis")**:
            - Focuses on testing boundary values of ordered partitions
            - String length boundaries (minLength, maxLength)
            - Numeric value boundaries (minimum, maximum)
            - Array count boundaries (minItems, maxItems)
            - Supports 2-value BVA (boundary + 1 neighbor) or 3-value BVA (boundary + 2 neighbors)
            - Coverage: (boundaries tested / total boundaries) * 100%
            
            Args:
                request: TestGenerationRequest with:
                    - swagger_analysis_file: Path to swagger analysis JSON
                    - technique: "equivalence_partitioning" or "boundary_value_analysis"
                    - bva_version: "2-value" or "3-value" (only for BVA)
                    - endpoint_filter: Optional endpoint path filter
                    - method_filter: Optional HTTP method filter
                    - save_output: Save results to JSON files
                
            Returns:
                Test generation results with all test cases in JSON format
            """
            try:
                if request.technique == "equivalence_partitioning":
                    result = await self.orchestrator.generate_equivalence_partition_tests(
                        swagger_analysis_file=request.swagger_analysis_file,
                        endpoint_filter=request.endpoint_filter,
                        method_filter=request.method_filter,
                        save_output=request.save_output
                    )
                elif request.technique == "boundary_value_analysis":
                    result = await self.orchestrator.generate_boundary_value_tests(
                        swagger_analysis_file=request.swagger_analysis_file,
                        bva_version=request.bva_version,
                        endpoint_filter=request.endpoint_filter,
                        method_filter=request.method_filter,
                        save_output=request.save_output
                    )
                else:
                    raise ValueError(f"Unsupported technique: {request.technique}")
                
                import json
                return json.dumps(result, indent=2)
            except Exception as e:
                raise
        
        @self.mcp.tool()
        async def generate_karate_features(request: KarateGenerationRequest) -> str:
            """
            Generate Karate feature files from test cases for API automation.
            
            This tool converts test case JSON files into executable Karate features:
            - Creates one .feature file per endpoint
            - Generates Gherkin syntax (Given-When-Then)
            - Uses Scenario Outline for data-driven testing
            - Applies tags: @smoke (success), @negative (failures), @regression (all)
            - Groups test cases by HTTP status codes
            - Generates karate-config.js with:
              * UUID generators for headers
              * Environment-specific base URLs
              * Common header configurations
              * Helper functions
            
            Output structure:
            - output/functional/karate-config.js
            - output/functional/features/{resource}/METHOD_endpoint.feature
            
            Args:
                request: KarateGenerationRequest with test cases directory and base URL
                
            Returns:
                Generation results with feature file paths and summary
            """
            try:
                result = await self.orchestrator.generate_karate_features(
                    test_cases_directory=request.test_cases_directory,
                    base_url=request.base_url,
                    output_directory=request.output_directory
                )
                
                import json
                return json.dumps(result, indent=2)
            except Exception as e:
                raise
    
    def get_mcp_app(self):
        """Get the FastMCP application instance"""
        return self.mcp