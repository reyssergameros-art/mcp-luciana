"""Utilidades centralizadas para operaciones de archivos y JSON.

Este módulo elimina duplicación de código relacionado con:
- Creación de directorios
- Lectura/escritura de JSON
- Generación de metadata
- Operaciones comunes de Path
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from ..constants import JSONConfig, VersionInfo

logger = logging.getLogger(__name__)


class FileOperations:
    """Centraliza operaciones de archivos y JSON para eliminar duplicación."""
    
    # Usar constantes centralizadas
    JSON_INDENT = JSONConfig.INDENT
    JSON_ENSURE_ASCII = JSONConfig.ENSURE_ASCII
    JSON_ENCODING = JSONConfig.ENCODING
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """
        Crea directorio si no existe (equivalente a mkdir -p).
        
        Args:
            path: Path del directorio a crear
            
        Returns:
            Path del directorio creado
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise
    
    @staticmethod
    def save_json(
        data: Dict[str, Any],
        file_path: Path,
        indent: Optional[int] = None,
        ensure_ascii: Optional[bool] = None
    ) -> Path:
        """
        Guarda diccionario como JSON con formato consistente.
        
        Args:
            data: Diccionario a guardar
            file_path: Path del archivo destino
            indent: Indentación (default: 2)
            ensure_ascii: Escapar caracteres no-ASCII (default: False)
            
        Returns:
            Path del archivo guardado
            
        Raises:
            IOError: Si falla la escritura del archivo
        """
        # Usar valores por defecto si no se especifican
        indent = indent if indent is not None else FileOperations.JSON_INDENT
        ensure_ascii = ensure_ascii if ensure_ascii is not None else FileOperations.JSON_ENSURE_ASCII
        
        try:
            # Asegurar que el directorio padre existe
            FileOperations.ensure_directory(file_path.parent)
            
            # Escribir JSON
            with open(file_path, 'w', encoding=FileOperations.JSON_ENCODING) as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            
            logger.debug(f"JSON saved successfully: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save JSON to {file_path}: {e}")
            raise
    
    @staticmethod
    def load_json(file_path: Path) -> Dict[str, Any]:
        """
        Carga JSON desde archivo con validaciones.
        
        Args:
            file_path: Path del archivo a cargar
            
        Returns:
            Diccionario con el contenido del JSON
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el JSON es inválido
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            with open(file_path, 'r', encoding=FileOperations.JSON_ENCODING) as f:
                data = json.load(f)
            
            logger.debug(f"JSON loaded successfully: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load JSON from {file_path}: {e}")
            raise
    
    @staticmethod
    def create_metadata(
        source: str,
        technique: Optional[str] = None,
        tool_version: str = None,
        additional_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea metadata estándar para archivos de output.
        
        Args:
            source: Fuente de los datos (URL o path)
            technique: Técnica utilizada (opcional)
            tool_version: Versión de la herramienta
            additional_fields: Campos adicionales a incluir
            
        Returns:
            Diccionario con metadata estándar
        """
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "source": source,
            "tool_version": tool_version or VersionInfo.TOOL_VERSION
        }
        
        if technique:
            metadata["technique"] = technique
        
        if additional_fields:
            metadata.update(additional_fields)
        
        return metadata
    
    @staticmethod
    def validate_file_exists(file_path: Path) -> Path:
        """
        Valida que un archivo existe y es accesible.
        
        Args:
            file_path: Path del archivo a validar
            
        Returns:
            Path validado
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el path no es un archivo
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        return file_path
    
    @staticmethod
    def validate_directory_exists(dir_path: Path) -> Path:
        """
        Valida que un directorio existe y es accesible.
        
        Args:
            dir_path: Path del directorio a validar
            
        Returns:
            Path validado
            
        Raises:
            FileNotFoundError: Si el directorio no existe
            ValueError: Si el path no es un directorio
        """
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")
        
        return dir_path
    
    @staticmethod
    def get_file_size_mb(file_path: Path) -> float:
        """
        Obtiene el tamaño de un archivo en megabytes.
        
        Args:
            file_path: Path del archivo
            
        Returns:
            Tamaño en MB
        """
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
