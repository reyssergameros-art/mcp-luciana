"""Configuración centralizada de logging para el proyecto."""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "mcp_swagger.log",
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """
    Configura el sistema de logging para toda la aplicación.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log (None para deshabilitar)
        enable_console: Habilitar output a consola
        enable_file: Habilitar output a archivo
    """
    # Configurar formato de log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Crear formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Obtener logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Handler para archivo
    if enable_file and log_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / log_file,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger (típicamente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# Configurar logging al importar el módulo
def configure_from_settings():
    """Configura logging usando settings de la aplicación."""
    try:
        from src.shared.config import settings
        setup_logging(
            log_level=settings.log_level,
            enable_console=True,
            enable_file=settings.enable_detailed_logging
        )
    except ImportError:
        # Fallback si settings no está disponible
        setup_logging(log_level="INFO")


# Inicializar logging automáticamente
configure_from_settings()
