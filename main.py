#!/usr/bin/env python3
"""
MCP Server - Swagger Analysis Tool
"""

import sys
from pathlib import Path

# Simple path setup
sys.path.insert(0, str(Path(__file__).parent))

from src.shared.config import settings, SwaggerConstants
from src.presentation.mcp_server import SwaggerAnalysisMCPServer


def main():
    """Main entry point for the MCP server"""
    try:
        server = SwaggerAnalysisMCPServer()
        mcp_app = server.get_mcp_app()
        
        mcp_app.run()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()