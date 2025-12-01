#!/usr/bin/env python3
"""
MCP Server - Swagger Analysis Tool
"""

import sys
import logging
from pathlib import Path

# Simple path setup
sys.path.insert(0, str(Path(__file__).parent))

from src.shared.logging_config import setup_logging
from src.shared.config import settings, SwaggerConstants
from src.presentation.mcp_server import SwaggerAnalysisMCPServer

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server"""
    # Configurar logging
    setup_logging(
        log_level=settings.log_level,
        enable_console=True,
        enable_file=settings.enable_detailed_logging
    )
    
    try:
        logger.info(f"Starting {settings.server_name} v{settings.server_version}")
        server = SwaggerAnalysisMCPServer()
        mcp_app = server.get_mcp_app()
        
        logger.info("MCP Server initialized successfully")
        mcp_app.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error starting server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()