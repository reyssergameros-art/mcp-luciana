"""Result aggregation utilities for test generation metrics.

This module extracts aggregation logic from MCPToolsOrchestrator
to respect Single Responsibility Principle.
"""
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ResultAggregator:
    """
    Centraliza cálculo de métricas agregadas de resultados.
    
    Responsibilities:
    - Calcular totales de test cases
    - Calcular promedios de coverage
    - Generar summaries de resultados
    
    Respects SRP: Solo se encarga de agregar y calcular métricas.
    """
    
    @staticmethod
    def aggregate_test_generation_metrics(results: List) -> Dict[str, Any]:
        """
        Agrega métricas de múltiples TestGenerationResult.
        
        Args:
            results: Lista de TestGenerationResult
            
        Returns:
            Diccionario con métricas agregadas
        """
        if not results:
            return {
                "total_endpoints": 0,
                "total_test_cases": 0,
                "total_partitions": 0,
                "average_coverage": 0.0
            }
        
        total_test_cases = sum(len(r.test_cases) for r in results)
        total_partitions = sum(r.total_partitions for r in results)
        avg_coverage = sum(r.coverage_percentage for r in results) / len(results)
        
        return {
            "total_endpoints": len(results),
            "total_test_cases": total_test_cases,
            "total_partitions": total_partitions,
            "average_coverage": round(avg_coverage, 2)
        }
    
    @staticmethod
    def aggregate_bva_metrics(results: List) -> Dict[str, Any]:
        """
        Agrega métricas de múltiples BVAResult.
        
        Args:
            results: Lista de BVAResult
            
        Returns:
            Diccionario con métricas agregadas de BVA
        """
        if not results:
            return {
                "total_endpoints": 0,
                "total_test_cases": 0,
                "total_boundaries": 0,
                "average_coverage": 0.0
            }
        
        total_test_cases = sum(len(r.test_cases) for r in results)
        total_boundaries = sum(r.boundaries_identified for r in results)
        avg_coverage = sum(r.coverage_percentage for r in results) / len(results)
        
        return {
            "total_endpoints": len(results),
            "total_test_cases": total_test_cases,
            "total_boundaries": total_boundaries,
            "average_coverage": round(avg_coverage, 2)
        }
    
    @staticmethod
    def aggregate_unified_metrics(results: List) -> Dict[str, Any]:
        """
        Agrega métricas de múltiples UnifiedTestResult.
        
        Args:
            results: Lista de UnifiedTestResult
            
        Returns:
            Diccionario con métricas agregadas unificadas
        """
        if not results:
            return {
                "total_endpoints": 0,
                "total_test_cases": 0,
                "techniques_applied": []
            }
        
        total_test_cases = sum(len(r.test_cases) for r in results)
        
        # Recolectar todas las técnicas únicas aplicadas
        techniques_applied = list(set(
            technique 
            for result in results 
            for technique in result.techniques_applied
        ))
        
        return {
            "total_endpoints": len(results),
            "total_test_cases": total_test_cases,
            "techniques_applied": techniques_applied
        }
    
    @staticmethod
    def create_response_summary(
        success: bool,
        total_items: int,
        item_type: str,
        additional_metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Crea un resumen estándar de respuesta.
        
        Args:
            success: Si la operación fue exitosa
            total_items: Cantidad total de items procesados
            item_type: Tipo de items (endpoints, test_cases, features, etc.)
            additional_metrics: Métricas adicionales opcionales
            
        Returns:
            Diccionario con estructura de respuesta estándar
        """
        response = {
            "success": success,
            "summary": {
                f"total_{item_type}": total_items
            }
        }
        
        if additional_metrics:
            response["summary"].update(additional_metrics)
        
        return response
    
    @staticmethod
    def calculate_success_failure_split(test_cases: List) -> Dict[str, int]:
        """
        Calcula split de test cases exitosos vs fallidos.
        
        Args:
            test_cases: Lista de test cases con expected_status_code
            
        Returns:
            Diccionario con conteos de success y failure
        """
        success_codes = {200, 201, 204}
        
        success_count = sum(
            1 for tc in test_cases 
            if getattr(tc, 'expected_status_code', 400) in success_codes
        )
        failure_count = len(test_cases) - success_count
        
        return {
            "success_test_cases": success_count,
            "failure_test_cases": failure_count,
            "total_test_cases": len(test_cases)
        }
