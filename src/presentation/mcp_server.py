"""MCP Server for Swagger Analysis Tool using FastMCP."""

import json
from pathlib import Path
from fastmcp import FastMCP
from pydantic import BaseModel, field_validator
from typing import Optional

from src.shared.config import get_config_manager, ConfigManager
from src.tools.mcp_tools import MCPToolsOrchestrator


class SwaggerAnalysisRequest(BaseModel):
    """Request model for Swagger analysis
    
    Accepts:
    - HTTP/HTTPS URLs: http://localhost:8080/v3/api-docs
    - Local JSON files: C:\\Users\\user\\swagger.json or swagger.json (relative)
    - Local YAML files: C:\\Users\\user\\swagger.yaml or swagger.yaml (relative)
    - File URIs: file://C:/Users/user/swagger.json
    """
    swagger_url: str
    format: Optional[str] = None  # "detailed" or "summary" - defaults from config
    save_output: Optional[bool] = True  # Save to JSON file
    output_format: Optional[str] = None  # "console", "file", or "both" - defaults from config
    
    def model_post_init(self, __context) -> None:
        """Set defaults from configuration after initialization."""
        config = get_config_manager()
        if self.format is None:
            self.format = config.swagger_analysis.get_default_format()
        if self.output_format is None:
            self.output_format = config.swagger_analysis.get_default_output_format()
    
    @field_validator('swagger_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is either a valid HTTP(S) URL or an existing JSON/YAML file path."""
        # Accept HTTP(S) URLs
        if v.startswith('http://') or v.startswith('https://'):
            return v
        
        # Handle file paths (with or without file:// prefix)
        file_path = v.replace('file://', '') if v.startswith('file://') else v
        path = Path(file_path)
        
        # Convert to absolute path if relative
        if not path.is_absolute():
            path = Path.cwd() / file_path
        
        # Validate file existence
        if not path.exists():
            raise ValueError(
                f"File path does not exist: {file_path}\n"
                f"Resolved absolute path: {path}\n"
                f"Supported formats: .json, .yaml, .yml"
            )
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Validate file extension for local files
        valid_extensions = ['.json', '.yaml', '.yml']
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Invalid file extension '{path.suffix}'. "
                f"Supported formats: {', '.join(valid_extensions)}\n"
                f"File: {path}"
            )
        
        return v
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v: Optional[str]) -> str:
        """Validate format is either 'detailed' or 'summary'."""
        if v is None:
            return None
        config = get_config_manager()
        if not config.swagger_analysis.validate_format(v):
            valid_formats = ', '.join(config.swagger_analysis.VALID_FORMATS)
            raise ValueError(f"Format must be one of: {valid_formats}")
        return v
    
    @field_validator('output_format')
    @classmethod
    def validate_output_format(cls, v: Optional[str]) -> str:
        """Validate output_format is 'console', 'file', or 'both'."""
        if v is None:
            return None
        config = get_config_manager()
        if not config.swagger_analysis.validate_output_format(v):
            valid_formats = ', '.join(config.swagger_analysis.VALID_OUTPUT_FORMATS)
            raise ValueError(f"output_format must be one of: {valid_formats}")
        return v


class TestGenerationRequest(BaseModel):
    """
    Request model for test case generation using ISTQB v4 techniques.
    
    Automatically applies both Equivalence Partitioning and Boundary Value Analysis.
    Generates one unified file per endpoint with all test cases from both techniques.
    """
    swagger_analysis_file: str
    bva_version: Optional[str] = None  # "2-value", "3-value", or "both" - defaults from config
    endpoint_filter: Optional[str] = None
    method_filter: Optional[str] = None
    save_output: Optional[bool] = True
    
    def model_post_init(self, __context) -> None:
        """Set defaults from configuration after initialization."""
        config = get_config_manager()
        if self.bva_version is None:
            self.bva_version = config.test_generation.get_default_bva_version()
    
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
    
    @field_validator('bva_version')
    @classmethod
    def validate_bva_version(cls, v: Optional[str]) -> str:
        """Validate BVA version."""
        if v is None:
            return None
        config = get_config_manager()
        if not config.test_generation.validate_bva_version(v):
            valid_versions = ', '.join(config.test_generation.VALID_BVA_VERSIONS)
            raise ValueError(f"BVA version must be one of: {valid_versions}")
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
    base_url: Optional[str] = None  # Defaults from config
    output_directory: Optional[str] = None
    
    def model_post_init(self, __context) -> None:
        """Set defaults from configuration after initialization."""
        config = get_config_manager()
        if self.base_url is None:
            self.base_url = config.api.get_default_base_url()
    
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
        if v is None:
            return None
        
        config = get_config_manager()
        if not config.api.validate_protocol(v):
            valid_protocols = ', '.join(config.api.VALID_PROTOCOLS)
            raise ValueError(f"base_url must start with one of: {valid_protocols}://")
        
        return v


class SwaggerAnalysisMCPServer:
    """MCP Server for Swagger Analysis Tool"""
    
    def __init__(self, config_manager: ConfigManager = None):
        """Initialize MCP Server with dependency injection."""
        self.config = config_manager or get_config_manager()
        self.mcp = FastMCP("MCP-Swagger-Analysis")
        self.orchestrator = MCPToolsOrchestrator(config_manager=self.config)
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
                
                return json.dumps(result, indent=2)
            except Exception as e:
                raise
        
        @self.mcp.tool()
        async def generate_test_cases(request: TestGenerationRequest) -> str:
            """
            Generate test cases using ISTQB v4 testing techniques.
            
            **IMPORTANT**: This tool automatically generates test cases using BOTH techniques 
            (Equivalence Partitioning + Boundary Value Analysis) in a unified output.
            Each endpoint gets ONE file containing all test cases from both techniques.
            
            **Techniques Applied Automatically**:
            
            1. **Equivalence Partitioning**:
               - Identifies valid and invalid equivalence partitions
               - Creates positive tests (all valid inputs)
               - Creates negative tests (one invalid input at a time)
               - Achieves 100% partition coverage (ISTQB requirement)
               - Applied to ALL HTTP methods: GET, POST, PUT, DELETE, PATCH
            
            2. **Boundary Value Analysis (2-value AND 3-value)**:
               - Tests boundary values of ordered partitions
               - String length boundaries (minLength, maxLength)
               - Numeric value boundaries (minimum, maximum)
               - Array count boundaries (minItems, maxItems)
               - 2-value BVA: Tests boundary + 1 neighbor value
               - 3-value BVA: Tests boundary + 2 neighbor values
               - Applied to ALL HTTP methods including GET (query params) and DELETE (path params)
               - Coverage: (boundaries tested / total boundaries) * 100%
            
            **Output**: One unified JSON file per endpoint with test cases from ALL techniques.
            Compatible with karate_generation tool for automation.
            
            Args:
                request: TestGenerationRequest with:
                    - swagger_analysis_file: Path to swagger analysis JSON (required)
                    - bva_version: "2-value", "3-value", or "both" (default: "both")
                    - endpoint_filter: Optional endpoint path filter
                    - method_filter: Optional HTTP method filter
                    - save_output: Save results to JSON files (default: true)
                
            Returns:
                Test generation results with all test cases from all techniques in JSON format
            """
            try:
                # Always use unified mode with both techniques for comprehensive coverage
                result = await self.orchestrator.generate_test_cases_unified(
                    swagger_analysis_file=request.swagger_analysis_file,
                    techniques=["equivalence_partitioning", "boundary_value_analysis"],
                    bva_version=request.bva_version,
                    endpoint_filter=request.endpoint_filter,
                    method_filter=request.method_filter,
                    save_output=request.save_output
                )
                
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
                
                return json.dumps(result, indent=2)
            except Exception as e:
                raise
    
    def get_mcp_app(self):
        """Get the FastMCP application instance"""
        return self.mcp